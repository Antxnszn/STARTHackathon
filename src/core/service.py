"""
Core Service - Business Logic & Orchestration
"""
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import logging

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
from src.geo.service import GeoService
from src.geo.schemas.requests import GeoAnalysisRequest
from src.env.service import EnvService
from src.env.schemas.requests import EnvAnalysisRequest
from src.config import settings

logger = logging.getLogger(__name__)


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
        
        # Initialize service dependencies
        self.geo_service = GeoService()
        self.env_service = EnvService()
    
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
        1. Geometry validation and deforestation check (GeoService)
        2. Environmental analysis (EnvService: water, climate, carbon)
        3. Compliance decision
        """
        if project_id not in self._projects:
            raise ValueError(f"Project {project_id} not found")
        
        if project_id not in self._geometries:
            raise ValueError(f"No geometry uploaded for project {project_id}")
        
        self._projects[project_id]["status"] = "PROCESSING"
        
        try:
            geometry = self._geometries[project_id]
            
            # Parse cutoff date from config
            cutoff_date = date.fromisoformat(settings.eudr_cutoff_date)
            
            # Step 1: Geo-spatial analysis (deforestation check)
            logger.info(f"Running geo analysis for project {project_id}")
            geo_request = GeoAnalysisRequest(
                project_id=project_id,
                geometry=geometry,
                cutoff_date=cutoff_date
            )
            geo_result = await self.geo_service.analyze(geo_request)
            
            # Extract geo results
            area_hectares = geo_result.area_hectares
            centroid = geo_result.centroid
            deforestation_analysis = geo_result.deforestation_analysis
            geometry_valid = geo_result.geometry_valid
            
            # Step 2: Environmental analysis (water, climate, carbon)
            logger.info(f"Running environmental analysis for project {project_id}")
            env_request = EnvAnalysisRequest(
                project_id=project_id,
                centroid=centroid,
                area_hectares=area_hectares,
                has_deforestation=not deforestation_analysis.is_deforestation_free
            )
            env_result = await self.env_service.analyze(env_request)
            
            # Map results to Core response format
            deforestation = DeforestationResult(
                is_deforestation_free=deforestation_analysis.is_deforestation_free,
                alerts_count=deforestation_analysis.alerts_count,
                total_loss_ha_post_cutoff=deforestation_analysis.total_loss_ha_post_cutoff,
                analysis_period_start=deforestation_analysis.analysis_period.start.isoformat(),
                analysis_period_end=deforestation_analysis.analysis_period.end.isoformat()
            )
            
            water_analysis = env_result.water_analysis
            water = WaterResult(
                risk_level=water_analysis.risk_level,
                risk_score=water_analysis.risk_score,
                in_veda_zone=water_analysis.in_veda_zone,
                aquifer_name=water_analysis.aquifer_name
            )
            
            climate_analysis = env_result.climate_analysis
            climate = ClimateResult(
                avg_annual_precipitation_mm=climate_analysis.avg_annual_precipitation_mm,
                avg_temperature_celsius=climate_analysis.avg_temperature_celsius,
                precipitation_suitable=climate_analysis.precipitation_suitable
            )
            
            carbon_analysis = env_result.carbon_analysis
            carbon = CarbonResult(
                estimated_co2e_tonnes=carbon_analysis.estimated_co2e_tonnes,
                calculation_applicable=carbon_analysis.calculation_applicable,
                reason=carbon_analysis.reason
            )
            
            # Determine compliance status
            is_compliant = (
                deforestation.is_deforestation_free and
                not water.in_veda_zone and
                water.risk_score < 4.0 and  # Not extreme risk
                geometry_valid
            )
            
            status = "COMPLIANT" if is_compliant else "NON_COMPLIANT"
            self._projects[project_id]["status"] = status
            self._projects[project_id]["updated_at"] = datetime.utcnow()
            
            # Build compliance summary
            issues = []
            if not deforestation.is_deforestation_free:
                issues.append(f"Deforestation detected: {deforestation.total_loss_ha_post_cutoff:.2f} ha lost")
            if water.in_veda_zone:
                issues.append(f"In veda zone: {water.aquifer_name}")
            if water.risk_score >= 4.0:
                issues.append(f"Extreme water risk: {water.risk_score:.1f}")
            if not geometry_valid:
                issues.append("Geometry validation failed")
            
            compliance_summary = (
                "All checks passed. Parcel is EUDR compliant."
                if is_compliant
                else f"Compliance issues: {', '.join(issues)}"
            )
            
            result = AnalysisResultResponse(
                project_id=project_id,
                status=status,
                compliance_summary=compliance_summary,
                area_hectares=area_hectares,
                geometry_valid=geometry_valid,
                deforestation=deforestation,
                water=water,
                climate=climate,
                carbon=carbon,
                analyzed_at=datetime.utcnow()
            )
            
            self._results[project_id] = result.model_dump()
            logger.info(f"Analysis complete for project {project_id}: {status}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {e}", exc_info=True)
            self._projects[project_id]["status"] = "ERROR"
            self._projects[project_id]["updated_at"] = datetime.utcnow()
            
            # Return error result
            return AnalysisResultResponse(
                project_id=project_id,
                status="ERROR",
                compliance_summary=f"Analysis failed: {str(e)}",
                area_hectares=0.0,
                geometry_valid=False,
                deforestation=DeforestationResult(
                    is_deforestation_free=False,
                    alerts_count=0,
                    total_loss_ha_post_cutoff=0.0,
                    analysis_period_start="",
                    analysis_period_end=""
                ),
                water=WaterResult(
                    risk_level="Unknown",
                    risk_score=0.0,
                    in_veda_zone=False,
                    aquifer_name=None
                ),
                climate=ClimateResult(
                    avg_annual_precipitation_mm=0.0,
                    avg_temperature_celsius=0.0,
                    precipitation_suitable=False
                ),
                carbon=CarbonResult(
                    estimated_co2e_tonnes=0.0,
                    calculation_applicable=False,
                    reason=f"Analysis error: {str(e)}"
                ),
                analyzed_at=datetime.utcnow()
            )
    
    async def generate_eudr_report(self, project_id: str) -> Optional[EUDRReportResponse]:
        """Generate TRACES NT compatible EUDR report"""
        if project_id not in self._projects:
            return None
        
        project = self._projects[project_id]
        
        if project["status"] != "COMPLIANT":
            logger.warning(f"Cannot generate report for project {project_id}: status is {project['status']}")
            return None
        
        if project_id not in self._geometries:
            logger.warning(f"Cannot generate report for project {project_id}: no geometry")
            return None
        
        if project_id not in self._results:
            logger.warning(f"Cannot generate report for project {project_id}: no analysis results")
            return None
        
        # Get analysis results
        analysis_result = self._results[project_id]
        
        # Generate reference number
        year = datetime.utcnow().year
        seq = abs(hash(project_id)) % 100000  # Pseudo-random sequence
        reference = f"GP-{year}-MX-{seq:05d}"
        
        # Build compliance metadata
        compliance_metadata = {
            "engine": "GreenPass v1.0",
            "verification_timestamp": datetime.utcnow().isoformat() + "Z",
            "water_risk_assessment": "APPROVED" if analysis_result["water"]["risk_score"] < 4.0 else "REVIEW_REQUIRED",
            "water_risk_score": analysis_result["water"]["risk_score"],
            "area_hectares": analysis_result["area_hectares"],
            "deforestation_alerts": analysis_result["deforestation"]["alerts_count"],
            "carbon_footprint_tonnes": analysis_result["carbon"]["estimated_co2e_tonnes"]
        }
        
        report = EUDRReportResponse(
            submission_type="DDS_IMPORT",
            version="2.1",
            header={
                "reference_number": reference,
                "operator": {
                    "name": project["organization_name"],
                    "eori": project["organization_eori"],
                    "address": "Mexico"  # TODO: Add to project data model
                },
                "destination_market": project["destination_market"]
            },
            commodity={
                "hs_code": project["commodity_code"],
                "scientific_name": "Persea americana",
                "trade_name": "Hass Avocado",
                "quantity": {
                    "amount": 18500.50,  # TODO: Get from user input or project data
                    "unit": "KGM"
                }
            },
            geolocation=self._geometries[project_id],
            compliance={
                "deforestation_free_post_2020": analysis_result["deforestation"]["is_deforestation_free"],
                "relevant_legislation_check": True,
                "audit_metadata": compliance_metadata
            },
            greenpass_reference=reference,
            generated_at=datetime.utcnow()
        )
        
        logger.info(f"Generated EUDR report for project {project_id}: {reference}")
        return report
