"""
Geo Response Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

from src.shared.models.geojson import Centroid


class AnalysisPeriod(BaseModel):
    """Time period for analysis"""
    start: date
    end: date


class DeforestationAnalysis(BaseModel):
    """Deforestation analysis results from GFW"""
    is_deforestation_free: bool = Field(
        ..., description="True if no deforestation detected after cutoff"
    )
    alerts_count: int = Field(..., description="Number of GLAD/RADD alerts")
    total_loss_ha_post_cutoff: float = Field(
        ..., description="Total hectares lost after cutoff date"
    )
    analysis_period: AnalysisPeriod


class GeoAnalysisResponse(BaseModel):
    """Complete geo-spatial analysis response"""
    project_id: str
    geometry_valid: bool
    area_hectares: float
    centroid: Centroid
    deforestation_analysis: DeforestationAnalysis
    validation_issues: List[str] = Field(default_factory=list)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "geometry_valid": True,
                "area_hectares": 14.25,
                "centroid": {
                    "latitude": 19.411957,
                    "longitude": -102.048722
                },
                "deforestation_analysis": {
                    "is_deforestation_free": True,
                    "alerts_count": 0,
                    "total_loss_ha_post_cutoff": 0.0,
                    "analysis_period": {
                        "start": "2021-01-01",
                        "end": "2025-12-31"
                    }
                },
                "validation_issues": []
            }
        }
    }


class GeometryValidationResponse(BaseModel):
    """Response from geometry validation"""
    is_valid: bool
    fixed_geometry: Optional[dict] = None
    issues_fixed: List[str] = Field(default_factory=list)
    vertex_count: int
    needs_simplification: bool = Field(
        default=False,
        description="True if vertex count > 5000 (TRACES NT limit)"
    )
