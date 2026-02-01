"""
Geo Router - Internal Spatial Analysis Endpoints
"""
from fastapi import APIRouter, HTTPException

from src.geo.schemas.requests import GeoAnalysisRequest
from src.geo.schemas.responses import GeoAnalysisResponse
from src.geo.service import GeoService

router = APIRouter()
service = GeoService()


@router.post("/analyze", response_model=GeoAnalysisResponse)
async def analyze_geometry(request: GeoAnalysisRequest):
    """
    Analyze geometry for EUDR compliance.
    
    Performs:
    1. Geometry validation (closed polygon, no self-intersection)
    2. Area calculation
    3. Centroid calculation
    4. Deforestation check via Global Forest Watch
    
    Internal endpoint called by Core Orchestrator.
    """
    try:
        result = await service.analyze(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/validate")
async def validate_geometry(geometry: dict):
    """
    Validate and fix a GeoJSON geometry.
    
    Returns the fixed geometry and list of issues found.
    """
    result = await service.validate_geometry(geometry)
    return result
