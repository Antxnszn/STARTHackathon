"""
Pytest Configuration and Fixtures
"""
import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path

from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_approved_geojson():
    """Load sample approved parcel GeoJSON"""
    path = Path(__file__).parent.parent / "mocks" / "inputs" / "parcel_approved.geojson"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def sample_rejected_geojson():
    """Load sample rejected parcel GeoJSON"""
    path = Path(__file__).parent.parent / "mocks" / "inputs" / "parcel_rejected.geojson"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def sample_polygon():
    """Simple polygon geometry for testing"""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-102.048215, 19.412301],
                [-102.052100, 19.412550],
                [-102.052850, 19.408020],
                [-102.047500, 19.408100],
                [-102.048215, 19.412301]
            ]
        ]
    }


@pytest.fixture
def mock_gfw_no_alerts():
    """Load mock GFW response with no alerts"""
    path = Path(__file__).parent.parent / "mocks" / "responses" / "gfw_no_alerts.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def mock_gfw_with_alerts():
    """Load mock GFW response with alerts"""
    path = Path(__file__).parent.parent / "mocks" / "responses" / "gfw_with_alerts.json"
    with open(path) as f:
        return json.load(f)
