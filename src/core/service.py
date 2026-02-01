"""
Core Service - Business Logic & Orchestration
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.core.schemas.requests import ProjectCreate
from src.core.schemas.responses import (
    ProjectResponse,
    AnalysisResultResponse,
    EUDRReportResponse,
    DeforestationResult,
    WaterResult,
    ClimateResult,
    CarbonResult,
)


class CoreService:
    """
    Core Orchestrator Service
    
    Manages project lifecycle and coordinates analysis between Geo and Env engines.
    """
    
    def __init__(self):
        # In-memory storage for hackathon (replace with DB in production)
        self._projects: Dict[str, dict] = {}
        self._geometries: Dict[str, dict] = {}
        self._results: Dict[str, dict] = {}
    
    async def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        project = {
            "id": project_id,
            "name": data.name,
            "organization_name": data.organization_name,
            "organization_eori": data.organization_eori,
            "commodity_code": data.commodity_code,
            "destination_market": data.destination_market,
            "status": "CREATED",
            "has_geometry": False,
            "created_at": now,
            "updated_at": None,
        }
        
        self._projects[project_id] = project
        return ProjectResponse(**project)
    
    async def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        project = self._projects.get(project_id)
        if project:
            return ProjectResponse(**project)
        return None
    
    async def list_projects(
        self,
        org_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[ProjectResponse]:
        """List projects with optional filters"""
        projects = list(self._projects.values())
        
        if status:
            projects = [p for p in projects if p["status"] == status]
        
        # Apply limit
        projects = projects[:limit]
        
        return [ProjectResponse(**p) for p in projects]
    
    async def upload_geometry(self, project_id: str, geojson: dict) -> dict:
        """Store geometry for a project"""
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        self._geometries[project_id] = geojson
        self._projects[project_id]["has_geometry"] = True
        self._projects[project_id]["status"] = "UPLOADED"
        self._projects[project_id]["updated_at"] = datetime.utcnow()
        
        return {"success": True}
    
    async def run_analysis(self, project_id: str) -> AnalysisResultResponse:
        """
        Run full EUDR compliance analysis.
        
        This orchestrates:
        1. Geometry validation
        2. Geo Engine call (deforestation)
        3. Env Engine call (water, climate, carbon)
        4. Compliance decision
        """
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        if project_id not in self._geometries:
            raise ValueError(f"No geometry uploaded for project {project_id}")
        
        self._projects[project_id]["status"] = "PROCESSING"
        
        # TODO: Replace with actual service calls
        # For now, return mock compliant result
        
        # Mock analysis results
        deforestation = DeforestationResult(
            is_deforestation_free=True,
            alerts_count=0,
            total_loss_ha_post_cutoff=0.0,
            analysis_period_start="2021-01-01",
            analysis_period_end="2025-12-31"
        )
        
        water = WaterResult(
            risk_level="Low-Medium",
            risk_score=1.5,
            in_veda_zone=False,
            aquifer_name=None
        )
        
        climate = ClimateResult(
            avg_annual_precipitation_mm=850.5,
            avg_temperature_celsius=18.2,
            precipitation_suitable=True
        )
        
        carbon = CarbonResult(
            estimated_co2e_tonnes=0.0,
            calculation_applicable=False,
            reason="No deforestation detected"
        )
        
        # Determine compliance status
        is_compliant = (
            deforestation.is_deforestation_free and
            not water.in_veda_zone and
            water.risk_score < 4.0  # Not extreme risk
        )
        
        status = "COMPLIANT" if is_compliant else "NON_COMPLIANT"
        self._projects[project_id]["status"] = status
        self._projects[project_id]["updated_at"] = datetime.utcnow()
        
        result = AnalysisResultResponse(
            project_id=project_id,
            status=status,
            compliance_summary="All checks passed. Parcel is EUDR compliant." if is_compliant else "Compliance issues detected.",
            area_hectares=14.25,  # TODO: Calculate from geometry
            geometry_valid=True,
            deforestation=deforestation,
            water=water,
            climate=climate,
            carbon=carbon,
            analyzed_at=datetime.utcnow()
        )
        
        self._results[project_id] = result.model_dump()
        return result
    
    async def generate_eudr_report(self, project_id: str) -> Optional[EUDRReportResponse]:
        """Generate TRACES NT compatible EUDR report"""
        if project_id not in self._projects:
            return None
        
        project = self._projects[project_id]
        
        if project["status"] != "COMPLIANT":
            return None
        
        if project_id not in self._geometries:
            return None
        
        # Generate reference number
        year = datetime.utcnow().year
        seq = abs(hash(project_id)) % 100000  # Pseudo-random sequence
        reference = f"GP-{year}-MX-{seq:05d}"
        
        report = EUDRReportResponse(
            submission_type="DDS_IMPORT",
            version="2.1",
            header={
                "reference_number": reference,
                "operator": {
                    "name": project["organization_name"],
                    "eori": project["organization_eori"],
                    "address": "Mexico"  # TODO: Add to project data
                },
                "destination_market": project["destination_market"]
            },
            commodity={
                "hs_code": project["commodity_code"],
                "scientific_name": "Persea americana",
                "trade_name": "Hass Avocado",
                "quantity": {
                    "amount": 18500.50,  # TODO: Get from user input
                    "unit": "KGM"
                }
            },
            geolocation=self._geometries[project_id],
            compliance={
                "deforestation_free_post_2020": True,
                "relevant_legislation_check": True,
                "audit_metadata": {
                    "engine": "GreenPass v1.0",
                    "verification_timestamp": datetime.utcnow().isoformat() + "Z",
                    "water_risk_assessment": "APPROVED"
                }
            },
            greenpass_reference=reference,
            generated_at=datetime.utcnow()
        )
        
        return report
