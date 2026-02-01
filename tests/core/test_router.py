"""
Tests for Core API Endpoints
"""
import pytest


def test_health_check(client):
    """Test root health endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "GreenPass" in data["service"]


def test_detailed_health_check(client):
    """Test detailed health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "external_apis" in data


def test_create_project(client):
    """Test project creation"""
    project_data = {
        "name": "Test Huerta",
        "organization_name": "Test Org S.A.",
        "organization_eori": "MX1234567890",
        "commodity_code": "08044000",
        "destination_market": "NL"
    }
    
    response = client.post("/api/projects", json=project_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test Huerta"
    assert data["status"] == "CREATED"
    assert "id" in data


def test_create_project_invalid_eori(client):
    """Test project creation with invalid EORI"""
    project_data = {
        "name": "Test Huerta",
        "organization_name": "Test Org S.A.",
        "organization_eori": "invalid",  # Should fail validation
        "commodity_code": "08044000",
        "destination_market": "NL"
    }
    
    response = client.post("/api/projects", json=project_data)
    assert response.status_code == 422  # Validation error


def test_list_projects(client):
    """Test listing projects"""
    # First create a project
    project_data = {
        "name": "List Test Huerta",
        "organization_name": "Test Org S.A.",
        "organization_eori": "MX9876543210",
        "commodity_code": "08044000",
        "destination_market": "NL"
    }
    client.post("/api/projects", json=project_data)
    
    # Then list
    response = client.get("/api/projects")
    assert response.status_code == 200
    
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert data["total"] >= 1


def test_get_project_not_found(client):
    """Test getting non-existent project"""
    response = client.get("/api/projects/nonexistent-id")
    assert response.status_code == 404
