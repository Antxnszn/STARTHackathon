"""
Env Response Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class WaterAnalysis(BaseModel):
    """Water risk analysis result"""
    risk_level: str = Field(..., description="Risk level: Low, Low-Medium, Medium-High, High, Extremely High")
    risk_score: float = Field(..., ge=0, le=5, description="Numeric score 0-5")
    in_veda_zone: bool = Field(..., description="True if in CONAGUA veda zone")
    aquifer_name: Optional[str] = Field(None, description="Name of aquifer if in veda zone")
    baseline_water_stress: str = Field(default="", description="WRI baseline water stress category")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "risk_level": "Low-Medium",
                "risk_score": 1.5,
                "in_veda_zone": False,
                "aquifer_name": None,
                "baseline_water_stress": "Low (<10%)"
            }
        }
    }


class ClimateAnalysisPeriod(BaseModel):
    """Time period for climate analysis"""
    start: date
    end: date


class ClimateAnalysis(BaseModel):
    """Climate analysis result from historical weather data"""
    avg_annual_precipitation_mm: float = Field(..., description="Average annual precipitation in mm")
    avg_temperature_celsius: float = Field(..., description="Average temperature in °C")
    precipitation_suitable: bool = Field(..., description="True if precipitation is suitable for avocados")
    min_temperature_celsius: float = Field(default=0, description="Minimum recorded temperature")
    max_temperature_celsius: float = Field(default=0, description="Maximum recorded temperature")
    total_precipitation_mm: float = Field(default=0, description="Total precipitation in period")
    analysis_period: ClimateAnalysisPeriod
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "avg_annual_precipitation_mm": 850.5,
                "avg_temperature_celsius": 18.2,
                "precipitation_suitable": True,
                "min_temperature_celsius": 5.0,
                "max_temperature_celsius": 32.0,
                "total_precipitation_mm": 850.5,
                "analysis_period": {
                    "start": "2023-01-01",
                    "end": "2023-12-31"
                }
            }
        }
    }


class CarbonAnalysis(BaseModel):
    """Carbon footprint calculation result"""
    estimated_co2e_tonnes: float = Field(..., description="Estimated CO2 equivalent in tonnes")
    calculation_applicable: bool = Field(
        ..., description="Whether calculation was performed (only if deforestation)"
    )
    reason: str = Field(..., description="Explanation of calculation or why not applicable")
    emission_factor_used: Optional[str] = Field(None, description="Climatiq emission factor ID if used")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "estimated_co2e_tonnes": 0.0,
                "calculation_applicable": False,
                "reason": "No deforestation detected",
                "emission_factor_used": None
            }
        }
    }


class EnvAnalysisResponse(BaseModel):
    """Complete environmental analysis response"""
    project_id: str
    water_analysis: WaterAnalysis
    climate_analysis: ClimateAnalysis
    carbon_analysis: CarbonAnalysis
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "water_analysis": {
                    "risk_level": "Low-Medium",
                    "risk_score": 1.5,
                    "in_veda_zone": False,
                    "aquifer_name": None,
                    "baseline_water_stress": "Low (<10%)"
                },
                "climate_analysis": {
                    "avg_annual_precipitation_mm": 850.5,
                    "avg_temperature_celsius": 18.2,
                    "precipitation_suitable": True,
                    "analysis_period": {
                        "start": "2023-01-01",
                        "end": "2023-12-31"
                    }
                },
                "carbon_analysis": {
                    "estimated_co2e_tonnes": 0.0,
                    "calculation_applicable": False,
                    "reason": "No deforestation detected"
                }
            }
        }
    }
