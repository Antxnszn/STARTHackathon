"""
Geo Service - Spatial Analysis Business Logic
"""
from datetime import date, datetime
from typing import Dict, Any
import logging

from src.geo.schemas.requests import GeoAnalysisRequest
from src.geo.schemas.responses import (
    GeoAnalysisResponse,
    GeometryValidationResponse,
    DeforestationAnalysis,
    AnalysisPeriod,
)
from src.geo.clients.gfw_client import GFWClient
from src.shared.models.geojson import Centroid
from src.shared.geometry import (
    validate_and_fix_geometry,
    calculate_area_hectares,
    calculate_centroid,
    get_vertex_count,
    is_polygon_in_ocean,
)

logger = logging.getLogger(__name__)


class GeoService:
    """
    Geo-Spatial Analysis Service
    
    Handles geometry validation and deforestation checks via GFW.
    """
    
    def __init__(self):
        self.gfw_client = GFWClient()
    
    async def analyze(self, request: GeoAnalysisRequest) -> GeoAnalysisResponse:
        """
        Full geo-spatial analysis including deforestation check.
        """
        geometry = request.geometry
        
        # Handle FeatureCollection input
        if isinstance(geometry, dict):
            if geometry.get("type") == "FeatureCollection":
                if geometry.get("features"):
                    geometry = geometry["features"][0].get("geometry", geometry)
            elif geometry.get("type") == "Feature":
                geometry = geometry.get("geometry", geometry)
        
        # Validate and fix geometry
        fixed_geometry, issues = validate_and_fix_geometry(geometry)
        
        # Check if in valid location
        if is_polygon_in_ocean(fixed_geometry):
            issues.append("Geometry appears to be outside Mexico bounds")
        
        # Calculate metrics
        area_ha = calculate_area_hectares(fixed_geometry)
        centroid = calculate_centroid(fixed_geometry)
        
        # Run deforestation analysis
        deforestation = await self._check_deforestation(
            fixed_geometry,
            request.cutoff_date
        )
        
        return GeoAnalysisResponse(
            project_id=request.project_id,
            geometry_valid=len(issues) == 0 or all("Fixed" in i for i in issues),
            area_hectares=area_ha,
            centroid=centroid,
            deforestation_analysis=deforestation,
            validation_issues=issues
        )
    
    async def validate_geometry(self, geometry: dict) -> GeometryValidationResponse:
        """
        Validate geometry without running full analysis.
        """
        fixed_geometry, issues = validate_and_fix_geometry(geometry)
        vertex_count = get_vertex_count(fixed_geometry)
        
        return GeometryValidationResponse(
            is_valid=len(issues) == 0,
            fixed_geometry=fixed_geometry if issues else None,
            issues_fixed=issues,
            vertex_count=vertex_count,
            needs_simplification=vertex_count > 5000
        )
    
    async def _check_deforestation(
        self,
        geometry: dict,
        cutoff_date: date
    ) -> DeforestationAnalysis:
        """
        Check for deforestation using Global Forest Watch API.
        
        For hackathon: Uses mock data if API fails.
        """
        try:
            # Try to call GFW API
            # Limit end_year to 2024 (latest available data) or current year if earlier
            current_year = datetime.now().year
            end_year = min(current_year, 2024)  # GFW data typically available up to previous year
            
            logger.info(f"Checking deforestation from {cutoff_date.year + 1} to {end_year}")
            
            result = await self.gfw_client.check_tree_cover_loss(
                geometry=geometry,
                start_year=cutoff_date.year + 1,  # Year after cutoff
                end_year=end_year
            )
            
            # Debug: Log the raw response
            logger.info(f"GFW API response: {result}")
            
            # Process loss data - handle None values properly
            data = result.get("data", [])
            total_loss = 0.0
            for r in data:
                loss_ha = r.get("total_loss_ha")
                # Handle None, 0, or numeric values
                if loss_ha is not None:
                    try:
                        total_loss += float(loss_ha)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid loss_ha value: {loss_ha}")
            
            logger.info(f"Total loss calculated: {total_loss} ha from {len(data)} records")
            
            return DeforestationAnalysis(
                is_deforestation_free=total_loss == 0,
                alerts_count=len(data),
                total_loss_ha_post_cutoff=total_loss,
                analysis_period=AnalysisPeriod(
                    start=date(cutoff_date.year + 1, 1, 1),
                    end=date(end_year, 12, 31)
                )
            )
        except Exception as e:
            # On API error, be conservative: assume deforestation may exist
            # This prevents false positives (approving when there might be deforestation)
            logger.error(f"GFW API error - cannot verify deforestation status: {e}", exc_info=True)
            logger.warning("Falling back to conservative assumption: deforestation status UNKNOWN")
            
            # Return as NON-COMPLIANT when API fails (conservative approach)
            # This ensures we don't approve parcels when we can't verify
            current_year = datetime.now().year
            end_year = min(current_year, 2024)
            
            return DeforestationAnalysis(
                is_deforestation_free=False,  # Conservative: assume non-compliant if we can't verify
                alerts_count=0,
                total_loss_ha_post_cutoff=0.0,  # Unknown, but marked as non-compliant
                analysis_period=AnalysisPeriod(
                    start=date(cutoff_date.year + 1, 1, 1),
                    end=date(end_year, 12, 31)
                )
            )
