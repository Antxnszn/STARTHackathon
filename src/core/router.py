"""
Core Router - Public API Endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import uuid
import json

from src.core.schemas.requests import ProjectCreate, ProjectAnalyze
from src.core.schemas.responses import (
    ProjectResponse,
    ProjectListResponse,
    AnalysisResultResponse,
    EUDRReportResponse,
)
from src.core.service import CoreService

router = APIRouter()
service = CoreService()


@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """
    Create a new export project.
    
    This initializes a project record for tracking the EUDR compliance analysis.
    """
    result = await service.create_project(project)
    return result


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """List all projects, optionally filtered by organization or status"""
    projects = await service.list_projects(org_id=org_id, status=status, limit=limit)
    return ProjectListResponse(projects=projects, total=len(projects))


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details by ID"""
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/upload")
async def upload_geojson(
    project_id: str,
    file: UploadFile = File(..., description="GeoJSON file with parcel geometry")
):
    """
    Upload a GeoJSON file containing the parcel geometry.
    
    The file should contain a Polygon or FeatureCollection with Polygon features.
    """
    if not file.filename.endswith(('.geojson', '.json')):
        raise HTTPException(
            status_code=400,
            detail="File must be a GeoJSON file (.geojson or .json)"
        )
    
    try:
        content = await file.read()
        geojson_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    result = await service.upload_geometry(project_id, geojson_data)
    return {"message": "Geometry uploaded successfully", "project_id": project_id}


@router.post("/projects/{project_id}/analyze", response_model=AnalysisResultResponse)
async def analyze_project(project_id: str):
    """
    Trigger full EUDR compliance analysis.
    
    This orchestrates calls to:
    1. Geo Engine (deforestation check)
    2. Env Engine (water & climate check)
    
    And updates the project status based on results.
    """
    result = await service.run_analysis(project_id)
    return result


@router.get("/projects/{project_id}/report", response_model=EUDRReportResponse)
async def get_eudr_report(project_id: str):
    """
    Generate the EUDR Due Diligence Statement (DDS) report.
    
    Returns a JSON payload compatible with TRACES NT format.
    Only available for projects with COMPLIANT status.
    """
    report = await service.generate_eudr_report(project_id)
    if not report:
        raise HTTPException(
            status_code=400,
            detail="Report not available. Project may not be compliant or analysis not complete."
        )
    return report
