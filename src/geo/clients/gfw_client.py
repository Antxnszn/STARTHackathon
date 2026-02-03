"""
Global Forest Watch API Client

Documentation: https://data-api.globalforestwatch.org/
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from typing import List
import logging

from src.shared.http_client import BaseHTTPClient
from src.config import settings

logger = logging.getLogger(__name__)

class TreeCoverLossRecord(BaseModel):
    """Single record of tree cover loss"""
    total_loss_ha: float
    umd_tree_cover_loss__year: int


class GFWTreeCoverLossResponse(BaseModel):
    """Response from GFW tree cover loss query"""
    data: List[TreeCoverLossRecord]
    status: str


class GeostoreResponse(BaseModel):
    """Response from GFW geostore creation"""
    gfw_geostore_id: str
    gfw_area__ha: float
    gfw_bbox: List[float]


class GFWClient(BaseHTTPClient):
    """
    Client for Global Forest Watch Data API.
    
    Used to check for deforestation alerts (GLAD/RADD) and tree cover loss.
    """
    
    def __init__(self):
        super().__init__(
            base_url=settings.gfw_api_url,
            api_key=settings.gfw_api_key if settings.gfw_api_key else None,
            timeout=60.0  # GFW can be slow
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Override headers to use x-api-key instead of Bearer"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers
    
    async def create_geostore(self, geometry: dict) -> Dict[str, Any]:
        """
        Create a geostore from a geometry to use in subsequent queries.
        
        Returns geostore_id for use in spatial queries.
        """
        # Geostore creation usually DOES NOT require an API key, but passing it doesn't hurt
        response = await self.post("/geostore/", data={"geometry": geometry})
        return response.get("data", {})
    
    async def check_tree_cover_loss(
        self,
        geometry: dict,
        start_year: int = 2021,
        end_year: int = 2025
    ) -> Dict[str, Any]:
        """
        Check for tree cover loss within a geometry.
        
        Args:
            geometry: GeoJSON polygon
            start_year: First year to check (inclusive)
            end_year: Last year to check (inclusive)
        
        Returns:
            Dict with 'data' containing loss records by year
        """
        # First, create a geostore
        geostore_data = await self.create_geostore(geometry)
        geostore_id = geostore_data.get("gfw_geostore_id")
        
        if not geostore_id:
            raise ValueError("Failed to create geostore for geometry")
        
        # Query tree cover loss
        # Format SQL as single line with single spaces
        sql = (
            f"SELECT SUM(area__ha) as total_loss_ha, umd_tree_cover_loss__year "
            f"FROM data "
            f"WHERE umd_tree_cover_loss__year >= {start_year} "
            f"AND umd_tree_cover_loss__year <= {end_year} "
            f"GROUP BY umd_tree_cover_loss__year "
            f"ORDER BY umd_tree_cover_loss__year"
        )
        
        response = await self.get(
            "/dataset/umd_tree_cover_loss/latest/query/json",
            params={
                "sql": sql,
                "geostore_id": geostore_id
            }
        )
        return response
    
    async def check_glad_alerts(
        self,
        geometry: dict,
        start_date: str = "2021-01-01",
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check for GLAD deforestation alerts"""
        geostore_data = await self.create_geostore(geometry)
        geostore_id = geostore_data.get("gfw_geostore_id")
        
        if not geostore_id:
            raise ValueError("Failed to obtain geostore ID")
            
        sql = "SELECT COUNT(*) as alert_count, SUM(area__ha) as total_area_ha FROM data"
        
        response = await self.get(
            "/dataset/umd_glad_landsat_alerts/latest/query/json",
            params={"sql": sql, "geostore_id": geostore_id}
        )
        return response
