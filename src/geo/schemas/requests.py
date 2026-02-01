"""
Geo Request Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import date


class GeoAnalysisRequest(BaseModel):
    """Request for geo-spatial analysis"""
    project_id: str = Field(..., description="Project UUID")
    geometry: Any = Field(..., description="GeoJSON geometry (Polygon or FeatureCollection)")
    cutoff_date: date = Field(
        default=date(2020, 12, 31),
        description="EUDR cutoff date for deforestation check"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-102.048215, 19.412301],
                            [-102.049100, 19.412550],
                            [-102.048850, 19.411020],
                            [-102.048215, 19.412301]
                        ]
                    ]
                },
                "cutoff_date": "2020-12-31"
            }
        }
    }
