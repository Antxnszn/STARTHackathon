"""
Env Router - Environmental Analysis Endpoints
"""
from fastapi import APIRouter, HTTPException

from src.env.schemas.requests import EnvAnalysisRequest
from src.env.schemas.responses import EnvAnalysisResponse
from src.env.service import EnvService

router = APIRouter()
service = EnvService()


@router.post("/analyze", response_model=EnvAnalysisResponse)
async def analyze_environment(request: EnvAnalysisRequest):
    """
    Analyze environmental conditions for a location.
    
    Performs:
    1. Water risk assessment (WRI Aqueduct)
    2. Climate analysis (Open-Meteo historical weather)
    3. Carbon footprint calculation (Climatiq) if deforestation detected
    
    Internal endpoint called by Core Orchestrator.
    """
    try:
        result = await service.analyze(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/water-risk")
async def check_water_risk(lat: float, lon: float):
    """
    Quick water risk check for a point.
    
    Returns water stress and veda zone status.
    """
    result = await service.check_water_risk_point(lat, lon)
    return result


@router.get("/climate")
async def get_climate_data(
    lat: float,
    lon: float,
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31"
):
    """
    Get historical climate data for a location.
    
    Returns precipitation and temperature statistics.
    """
    result = await service.get_climate_data(lat, lon, start_date, end_date)
    return result
