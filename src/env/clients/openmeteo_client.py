"""
Open-Meteo Historical Weather API Client

Documentation: https://open-meteo.com/en/docs/historical-weather-api
Free API - No authentication required.
"""
from typing import Dict, Any, List
from pydantic import BaseModel

from src.shared.http_client import BaseHTTPClient
from src.config import settings


class OpenMeteoDaily(BaseModel):
    """Daily weather data"""
    time: List[str]
    precipitation_sum: List[float]
    temperature_2m_mean: List[float]


class OpenMeteoResponse(BaseModel):
    """Response from Open-Meteo historical API"""
    latitude: float
    longitude: float
    elevation: float
    timezone: str
    daily: OpenMeteoDaily


class OpenMeteoClient(BaseHTTPClient):
    """
    Client for Open-Meteo Historical Weather API.
    
    Free, no API key required.
    Used to get historical precipitation and temperature data.
    """
    
    def __init__(self):
        super().__init__(
            base_url=settings.openmeteo_api_url,
            api_key=None,  # No API key needed
            timeout=30.0
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Override to remove auth header"""
        return {
            "Accept": "application/json",
        }
    
    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        variables: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical weather data for a location.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            variables: Daily variables to fetch (default: precipitation, temperature)
        
        Returns:
            Dict with latitude, longitude, elevation, timezone, daily data
        """
        if variables is None:
            variables = [
                "precipitation_sum",
                "temperature_2m_mean",
                "temperature_2m_min",
                "temperature_2m_max",
            ]
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(variables),
            "timezone": "America/Mexico_City",
        }
        
        # Open-Meteo uses query params, not path
        response = await self.get("", params=params)
        return response
    
    async def get_annual_summary(
        self,
        latitude: float,
        longitude: float,
        year: int = 2023
    ) -> Dict[str, Any]:
        """
        Get annual weather summary for a location.
        
        Returns total precipitation and average temperature.
        """
        result = await self.get_historical_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=f"{year}-01-01",
            end_date=f"{year}-12-31"
        )
        
        daily = result.get("daily", {})
        precip = daily.get("precipitation_sum", [])
        temp = daily.get("temperature_2m_mean", [])
        
        # Filter out None values
        precip = [p for p in precip if p is not None]
        temp = [t for t in temp if t is not None]
        
        return {
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "year": year,
            "total_precipitation_mm": sum(precip) if precip else 0,
            "avg_temperature_celsius": sum(temp) / len(temp) if temp else 0,
            "data_points": len(temp),
        }
