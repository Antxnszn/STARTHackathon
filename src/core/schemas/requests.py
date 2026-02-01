"""
Core Request Schemas - API Input Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ProjectCreate(BaseModel):
    """Request to create a new project"""
    name: str = Field(..., min_length=3, max_length=255, description="Project name")
    organization_name: str = Field(..., description="Organization/company name")
    organization_eori: str = Field(
        ...,
        pattern=r"^[A-Z]{2}[0-9A-Z]{1,15}$",
        description="EORI number (MX + 10-15 chars)"
    )
    commodity_code: str = Field(default="08044000", description="HS Code (default: avocados)")
    destination_market: str = Field(
        default="NL",
        max_length=2,
        description="ISO country code of destination (e.g., NL, DE, FR)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Huerta San Miguel - Lote A",
                "organization_name": "Avocados From Mexico S.A.",
                "organization_eori": "MX123456789012",
                "commodity_code": "08044000",
                "destination_market": "NL"
            }
        }
    }


class ProjectAnalyze(BaseModel):
    """Request to analyze a project (optional params)"""
    cutoff_date: date = Field(
        default=date(2020, 12, 31),
        description="EUDR cutoff date for deforestation check"
    )
    force_reanalysis: bool = Field(
        default=False,
        description="Force re-run analysis even if already completed"
    )


class GeometryUpload(BaseModel):
    """Direct geometry upload (alternative to file upload)"""
    geometry: dict = Field(..., description="GeoJSON geometry or FeatureCollection")
    plot_id: Optional[str] = Field(None, description="Optional plot identifier")
