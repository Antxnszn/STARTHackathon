"""
Core Response Schemas - API Output Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ProjectResponse(BaseModel):
    """Project details response"""
    id: str
    name: str
    organization_name: str
    organization_eori: str
    commodity_code: str
    destination_market: str
    status: Literal["CREATED", "UPLOADED", "PROCESSING", "COMPLIANT", "NON_COMPLIANT", "ERROR"]
    has_geometry: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Huerta San Miguel - Lote A",
                "organization_name": "Avocados From Mexico S.A.",
                "organization_eori": "MX123456789012",
                "commodity_code": "08044000",
                "destination_market": "NL",
                "status": "CREATED",
                "has_geometry": False,
                "created_at": "2026-01-15T10:30:00Z"
            }
        }
    }


class ProjectListResponse(BaseModel):
    """List of projects"""
    projects: List[ProjectResponse]
    total: int


class DeforestationResult(BaseModel):
    """Deforestation analysis result"""
    is_deforestation_free: bool
    alerts_count: int
    total_loss_ha_post_cutoff: float
    analysis_period_start: str
    analysis_period_end: str


class WaterResult(BaseModel):
    """Water risk analysis result"""
    risk_level: str
    risk_score: float
    in_veda_zone: bool
    aquifer_name: Optional[str] = None


class ClimateResult(BaseModel):
    """Climate analysis result"""
    avg_annual_precipitation_mm: float
    avg_temperature_celsius: float
    precipitation_suitable: bool


class CarbonResult(BaseModel):
    """Carbon footprint result"""
    estimated_co2e_tonnes: float
    calculation_applicable: bool
    reason: str


class AnalysisResultResponse(BaseModel):
    """Complete analysis result"""
    project_id: str
    status: Literal["COMPLIANT", "NON_COMPLIANT", "ERROR"]
    compliance_summary: str
    area_hectares: float
    geometry_valid: bool
    deforestation: DeforestationResult
    water: WaterResult
    climate: ClimateResult
    carbon: CarbonResult
    analyzed_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "COMPLIANT",
                "compliance_summary": "All checks passed. Parcel is EUDR compliant.",
                "area_hectares": 14.25,
                "geometry_valid": True,
                "deforestation": {
                    "is_deforestation_free": True,
                    "alerts_count": 0,
                    "total_loss_ha_post_cutoff": 0.0,
                    "analysis_period_start": "2021-01-01",
                    "analysis_period_end": "2025-12-31"
                },
                "water": {
                    "risk_level": "Low-Medium",
                    "risk_score": 1.5,
                    "in_veda_zone": False,
                    "aquifer_name": None
                },
                "climate": {
                    "avg_annual_precipitation_mm": 850.5,
                    "avg_temperature_celsius": 18.2,
                    "precipitation_suitable": True
                },
                "carbon": {
                    "estimated_co2e_tonnes": 0.0,
                    "calculation_applicable": False,
                    "reason": "No deforestation detected"
                },
                "analyzed_at": "2026-01-15T11:00:00Z"
            }
        }
    }


class EUDRReportResponse(BaseModel):
    """EUDR DDS Report (TRACES NT format)"""
    submission_type: str = "DDS_IMPORT"
    version: str = "2.1"
    header: dict
    commodity: dict
    geolocation: dict
    compliance: dict
    
    # GreenPass metadata
    greenpass_reference: str
    generated_at: datetime
