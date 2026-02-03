"""
Tests for Geometry Utilities
"""
import pytest
from src.shared.geometry import (
    validate_and_fix_geometry,
    calculate_area_hectares,
    calculate_centroid,
    get_vertex_count,
    is_polygon_in_ocean,
)


def test_calculate_centroid(sample_polygon):
    """Test centroid calculation"""
    centroid = calculate_centroid(sample_polygon)
    
    # Should be roughly in the center of the polygon
    assert 19.4 < centroid.latitude < 19.42
    assert -102.06 < centroid.longitude < -102.04


def test_calculate_area_hectares(sample_polygon):
    """Test area calculation"""
    area = calculate_area_hectares(sample_polygon)
    
    # Area should be reasonable for an agricultural plot (> 0, < 1000 ha)
    assert area > 0
    assert area < 1000


def test_get_vertex_count(sample_polygon):
    """Test vertex counting"""
    count = get_vertex_count(sample_polygon)
    
    # Our sample polygon has 5 vertices (closed, first = last)
    assert count == 5


def test_is_polygon_in_ocean_valid():
    """Test ocean check for valid Mexican polygon"""
    # Michoacán polygon - should be valid
    polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-102.0, 19.4],
            [-102.1, 19.4],
            [-102.1, 19.3],
            [-102.0, 19.3],
            [-102.0, 19.4]
        ]]
    }
    
    assert not is_polygon_in_ocean(polygon)


def test_is_polygon_in_ocean_invalid():
    """Test ocean check for polygon outside Mexico"""
    # Pacific Ocean polygon - should be invalid
    polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-150.0, 10.0],
            [-150.1, 10.0],
            [-150.1, 9.9],
            [-150.0, 9.9],
            [-150.0, 10.0]
        ]]
    }
    
    assert is_polygon_in_ocean(polygon)


def test_validate_and_fix_unclosed_polygon():
    """Test fixing unclosed polygon"""
    unclosed = {
        "type": "Polygon",
        "coordinates": [[
            [-102.0, 19.4],
            [-102.1, 19.4],
            [-102.1, 19.3],
            [-102.0, 19.3]
            # Missing closing point
        ]]
    }
    
    fixed, issues = validate_and_fix_geometry(unclosed)
    
    # Should be fixed (closed)
    coords = fixed["coordinates"][0]
    assert coords[0] == coords[-1]
