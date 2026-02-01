"""
Climatiq Carbon Emissions API Client

Documentation: https://www.climatiq.io/docs/api-reference/estimate
Requires API key.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel

from src.shared.http_client import BaseHTTPClient
from src.config import settings


class ClimatiqEmissionFactor(BaseModel):
    """Emission factor details"""
    id: str
    name: str
    source: str
    year: int


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
        forest_type: str = "tropical_rainforest"
    ) -> Dict[str, Any]:
        """
        Estimate CO2e emissions from land use change (deforestation).
        
        Args:
            area_ha: Area in hectares
            forest_type: Type of forest (tropical_rainforest, temperate, etc.)
        
        Returns:
            Dict with co2e in kg and calculation details
        """
        # Climatiq activity ID for land use change
        activity_id = f"land_use_change-forests-type_{forest_type}"
        
        payload = {
            "emission_factor": {
                "activity_id": activity_id,
                "data_version": "^21"
            },
            "parameters": {
                "area": area_ha,
                "area_unit": "ha"
            }
        }
        
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
        # Map mode to Climatiq activity
        mode_map = {
            "sea_freight": "freight_transport-sea_freight-vessel_type_container_ship",
            "road_freight": "freight_transport-road-vehicle_type_hgv",
            "air_freight": "freight_transport-air_freight-flight_type_cargo",
        }
        
        activity_id = mode_map.get(mode, mode_map["sea_freight"])
        
        payload = {
            "emission_factor": {
                "activity_id": activity_id,
                "data_version": "^21"
            },
            "parameters": {
                "distance": distance_km,
                "distance_unit": "km",
                "weight": weight_tonnes,
                "weight_unit": "t"
            }
        }
        
        response = await self.post("/estimate", data=payload)
        return response
    
    async def search_emission_factors(
        self,
        query: str,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Search for available emission factors.
        
        Args:
            query: Search term
            category: Optional category filter
        
        Returns:
            List of matching emission factors
        """
        params = {"query": query}
        if category:
            params["category"] = category
        
        response = await self.get("/search", params=params)
        return response
