"""
Env Request Schemas
"""
from pydantic import BaseModel, Field

from src.shared.models.geojson import Centroid


class EnvAnalysisRequest(BaseModel):
    """Request for environmental analysis"""
    project_id: str = Field(..., description="Project UUID")
    centroid: Centroid = Field(..., description="Center point of the parcel")
    area_hectares: float = Field(..., description="Area in hectares")
    has_deforestation: bool = Field(
        default=False,
        description="Whether deforestation was detected (triggers CO2 calculation)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "centroid": {
                    "latitude": 19.411957,
                    "longitude": -102.048722
                },
                "area_hectares": 14.25,
                "has_deforestation": False
            }
        }
    }
