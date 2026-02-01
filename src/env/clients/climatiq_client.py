"""
Climatiq Carbon Emissions API Client

Documentation: https://www.climatiq.io/docs/api-reference/estimate
Requires API key.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from src.shared.http_client import BaseHTTPClient
from src.config import settings

logger = logging.getLogger(__name__)


# Emission factor IDs for land use change (UUIDs from Climatiq)
# These use the "AreaOverTime" unit type and require area + time parameters
EMISSION_FACTOR_IDS = {
    # Forest land converted to cropland - best for agricultural deforestation
    "forest_to_cropland": "71926a7e-bede-8739-9a82-804e67ae1a46",
    # Forest land converted to grasslands
    "forest_to_grassland": "c6d40a10-e042-86ce-97b3-a8ac0453872d",
    # Forest land converted to wetlands
    "forest_to_wetland": "f7bd1f3a-135d-820e-8e33-8204c42a7efe",
    # Lands converted to cropland (general)
    "land_to_cropland": "883218bd-6d83-8af2-b1c3-26f0f4fc8e2a",
}

# IPCC default emission factor for tropical forest (tonnes CO2e per hectare)
IPCC_DEFAULT_TROPICAL_FOREST_TCO2E_PER_HA = 500.0


class ClimatiqEmissionFactor(BaseModel):
    """Emission factor details"""
    id: str
    name: str
    source: Optional[str] = None
    year: Optional[int] = None
    activity_id: Optional[str] = None
    region: Optional[str] = None


class ClimatiqEstimateResponse(BaseModel):
    """Response from Climatiq estimate endpoint"""
    co2e: float
    co2e_unit: str
    co2e_calculation_method: str
    emission_factor: Optional[ClimatiqEmissionFactor] = None


class ClimatiqClient(BaseHTTPClient):
    """
    Client for Climatiq Carbon Emissions API.
    
    Used to calculate CO2e emissions from land use change (deforestation).
    
    Note: Climatiq uses two selector formats:
    1. By UUID: {"id": "uuid-here"} - no data_version needed
    2. By activity_id: {"activity_id": "...", "data_version": "^30"} 
    
    We use UUIDs for reliability as activity_ids can change between versions.
    """
    
    def __init__(self):
        super().__init__(
            base_url=settings.climatiq_api_url,
            api_key=settings.climatiq_api_key,
            timeout=30.0
        )
    
    async def estimate_land_use_emissions(
        self,
        area_ha: float,
        conversion_type: str = "forest_to_cropland"
    ) -> Dict[str, Any]:
        """
        Estimate CO2e emissions from land use change (deforestation).
        
        Args:
            area_ha: Area in hectares
            conversion_type: Type of land conversion:
                - "forest_to_cropland" (default, best for agriculture)
                - "forest_to_grassland"
                - "forest_to_wetland"
                - "land_to_cropland"
        
        Returns:
            Dict with co2e in kg and calculation details
        """
        factor_id = EMISSION_FACTOR_IDS.get(conversion_type, EMISSION_FACTOR_IDS["forest_to_cropland"])
        
        # Climatiq emission factors for land use change use "AreaOverTime" unit type
        # This requires both area and time parameters
        payload = {
            "emission_factor": {
                "id": factor_id  # Use UUID directly, no data_version needed
            },
            "parameters": {
                "area": area_ha,
                "area_unit": "ha",
                "time": 1,  # Assuming 1 year of conversion
                "time_unit": "year"
            }
        }
        
        logger.debug(f"Climatiq request: {payload}")
        response = await self.post("/estimate", data=payload)
        return response
    
    async def estimate_transport_emissions(
        self,
        distance_km: float,
        weight_tonnes: float,
        mode: str = "sea_freight"
    ) -> Dict[str, Any]:
        """
        Estimate CO2e emissions from transport.
        
        Useful for calculating supply chain emissions (optional).
        
        Args:
            distance_km: Distance in kilometers
            weight_tonnes: Weight of cargo in tonnes
            mode: Transport mode (sea_freight, road_freight, air_freight)
        
        Returns:
            Dict with co2e in kg and calculation details
        """
        # Map mode to Climatiq activity IDs (using activity_id + data_version format)
        mode_map = {
            "sea_freight": "freight_transport-sea_freight-vessel_type_container_ship",
            "road_freight": "freight_transport-road-vehicle_type_hgv",
            "air_freight": "freight_transport-air_freight-flight_type_cargo",
        }
        
        activity_id = mode_map.get(mode, mode_map["sea_freight"])
        
        payload = {
            "emission_factor": {
                "activity_id": activity_id,
                "data_version": "^30"  # Latest data version
            },
            "parameters": {
                "distance": distance_km,
                "distance_unit": "km",
                "weight": weight_tonnes,
                "weight_unit": "t"
            }
        }
        
        logger.debug(f"Climatiq transport request: {payload}")
        response = await self.post("/estimate", data=payload)
        return response
    
    async def search_emission_factors(
        self,
        query: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for available emission factors.
        
        Args:
            query: Search term
            category: Optional category filter (e.g., "Land Use Change")
        
        Returns:
            Dict with 'results' containing matching emission factors
        """
        params = {
            "query": query,
            "data_version": "^30",  # Required parameter
            "results_per_page": 20
        }
        if category:
            params["category"] = category
        
        response = await self.get("/search", params=params)
        return response
