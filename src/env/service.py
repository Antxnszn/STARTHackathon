"""
Env Service - Environmental Analysis Business Logic
"""
from datetime import date
from typing import Dict, Any

from src.env.schemas.requests import EnvAnalysisRequest
from src.env.schemas.responses import (
    EnvAnalysisResponse,
    WaterAnalysis,
    ClimateAnalysis,
    ClimateAnalysisPeriod,
    CarbonAnalysis,
)
from src.env.clients.openmeteo_client import OpenMeteoClient
from src.env.clients.climatiq_client import ClimatiqClient
from src.env.clients.aqueduct_client import AqueductClient


class EnvService:
    """
    Environmental Impact Analysis Service
    
    Handles water risk, climate analysis, and carbon footprint calculations.
    """
    
    def __init__(self):
        self.openmeteo = OpenMeteoClient()
        self.climatiq = ClimatiqClient()
        self.aqueduct = AqueductClient()
    
    async def analyze(self, request: EnvAnalysisRequest) -> EnvAnalysisResponse:
        """
        Full environmental analysis.
        """
        # Run all analyses
        water = await self._analyze_water(
            request.centroid.latitude,
            request.centroid.longitude
        )
        
        climate = await self._analyze_climate(
            request.centroid.latitude,
            request.centroid.longitude
        )
        
        carbon = await self._analyze_carbon(
            request.area_hectares,
            request.has_deforestation
        )
        
        return EnvAnalysisResponse(
            project_id=request.project_id,
            water_analysis=water,
            climate_analysis=climate,
            carbon_analysis=carbon
        )
    
    async def check_water_risk_point(self, lat: float, lon: float) -> WaterAnalysis:
        """Quick water risk check for a single point."""
        return await self._analyze_water(lat, lon)
    
    async def get_climate_data(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get raw climate data for a location."""
        return await self.openmeteo.get_historical_weather(
            lat, lon, start_date, end_date
        )
    
    async def _analyze_water(self, lat: float, lon: float) -> WaterAnalysis:
        """
        Analyze water risk using WRI Aqueduct data.
        
        Falls back to mock data for hackathon.
        """
        try:
            result = await self.aqueduct.get_water_risk(lat, lon)
            
            # Check veda zone (Mexican aquifer restrictions)
            veda_check = self.aqueduct.check_veda_zone(lat, lon)
            
            return WaterAnalysis(
                risk_level=result.get("overall_water_risk", "Low-Medium"),
                risk_score=result.get("overall_water_risk_score", 1.5),
                in_veda_zone=veda_check.get("in_veda", False),
                aquifer_name=veda_check.get("aquifer_name"),
                baseline_water_stress=result.get("baseline_water_stress", "Low (<10%)")
            )
        except Exception as e:
            print(f"Aqueduct error (using mock): {e}")
            return WaterAnalysis(
                risk_level="Low-Medium",
                risk_score=1.5,
                in_veda_zone=False,
                aquifer_name=None,
                baseline_water_stress="Low (<10%)"
            )
    
    async def _analyze_climate(self, lat: float, lon: float) -> ClimateAnalysis:
        """
        Analyze historical climate data.
        
        Checks if conditions are suitable for avocado cultivation.
        """
        try:
            # Get last year's data
            result = await self.openmeteo.get_historical_weather(
                lat, lon,
                start_date="2023-01-01",
                end_date="2023-12-31"
            )
            
            daily = result.get("daily", {})
            precip = daily.get("precipitation_sum", [])
            temp = daily.get("temperature_2m_mean", [])
            
            # Calculate statistics
            total_precip = sum(p for p in precip if p is not None)
            avg_temp = sum(t for t in temp if t is not None) / len(temp) if temp else 18.0
            min_temp = min((t for t in temp if t is not None), default=5.0)
            max_temp = max((t for t in temp if t is not None), default=32.0)
            
            # Avocados need 1000-2000mm annual rainfall
            # Optimal temp range: 16-22°C
            precipitation_suitable = 700 <= total_precip <= 2500
            
            return ClimateAnalysis(
                avg_annual_precipitation_mm=round(total_precip, 1),
                avg_temperature_celsius=round(avg_temp, 1),
                precipitation_suitable=precipitation_suitable,
                min_temperature_celsius=round(min_temp, 1),
                max_temperature_celsius=round(max_temp, 1),
                total_precipitation_mm=round(total_precip, 1),
                analysis_period=ClimateAnalysisPeriod(
                    start=date(2023, 1, 1),
                    end=date(2023, 12, 31)
                )
            )
        except Exception as e:
            print(f"Open-Meteo error (using mock): {e}")
            return ClimateAnalysis(
                avg_annual_precipitation_mm=850.0,
                avg_temperature_celsius=18.2,
                precipitation_suitable=True,
                min_temperature_celsius=5.0,
                max_temperature_celsius=32.0,
                total_precipitation_mm=850.0,
                analysis_period=ClimateAnalysisPeriod(
                    start=date(2023, 1, 1),
                    end=date(2023, 12, 31)
                )
            )
    
    async def _analyze_carbon(
        self,
        area_hectares: float,
        has_deforestation: bool
    ) -> CarbonAnalysis:
        """
        Calculate carbon footprint if deforestation was detected.
        
        Uses Climatiq API with tropical forest emission factors.
        """
        if not has_deforestation:
            return CarbonAnalysis(
                estimated_co2e_tonnes=0.0,
                calculation_applicable=False,
                reason="No deforestation detected",
                emission_factor_used=None
            )
        
        try:
            result = await self.climatiq.estimate_land_use_emissions(
                area_ha=area_hectares
            )
            
            co2e_kg = result.get("co2e", 0)
            co2e_tonnes = co2e_kg / 1000  # Convert kg to tonnes
            
            return CarbonAnalysis(
                estimated_co2e_tonnes=round(co2e_tonnes, 2),
                calculation_applicable=True,
                reason=f"Calculated for {area_hectares:.2f} ha of tropical forest loss",
                emission_factor_used=result.get("emission_factor", {}).get("id", "unknown")
            )
        except Exception as e:
            print(f"Climatiq error (using estimate): {e}")
            # Fallback: IPCC estimate ~500 tonnes CO2/ha for tropical forest
            estimated = area_hectares * 500
            return CarbonAnalysis(
                estimated_co2e_tonnes=round(estimated, 2),
                calculation_applicable=True,
                reason=f"Estimated using IPCC default (500 tCO2e/ha) for {area_hectares:.2f} ha",
                emission_factor_used="IPCC_default_tropical_forest"
            )
