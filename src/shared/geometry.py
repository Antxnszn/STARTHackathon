"""
Geometry Utilities - Shapely helpers for polygon validation
"""
from typing import Tuple, List
from shapely.geometry import shape, Polygon, Point, mapping
from shapely.validation import make_valid
from shapely.ops import orient

from src.shared.models.geojson import Centroid, PolygonGeometry


def validate_and_fix_geometry(geojson_dict: dict) -> Tuple[dict, List[str]]:
    """
    Validate and fix common geometry issues.
    
    Returns:
        Tuple of (fixed_geojson, list_of_issues_fixed)
    """
    issues = []
    geom = shape(geojson_dict)
    
    # Check if geometry is valid
    if not geom.is_valid:
        geom = make_valid(geom)
        issues.append("Fixed invalid geometry (self-intersection or other issues)")
    
    # Ensure counter-clockwise orientation for exterior ring
    if isinstance(geom, Polygon):
        geom = orient(geom, sign=1.0)  # Counter-clockwise
        if "orientation" not in str(issues):
            issues.append("Fixed ring orientation")
    
    # Convert back to GeoJSON
    fixed = mapping(geom)
    
    return fixed, issues


def calculate_area_hectares(geojson_dict: dict) -> float:
    """
    Calculate area in hectares from a GeoJSON geometry.
    Uses a simple approximation suitable for small agricultural plots.
    """
    from pyproj import Geod
    
    geom = shape(geojson_dict)
    
    # Use WGS84 ellipsoid for accurate area calculation
    geod = Geod(ellps='WGS84')
    
    if isinstance(geom, Polygon):
        area_m2 = abs(geod.geometry_area_perimeter(geom)[0])
    else:
        # For MultiPolygon, sum all areas
        area_m2 = sum(
            abs(geod.geometry_area_perimeter(p)[0])
            for p in geom.geoms
        )
    
    # Convert to hectares (1 ha = 10,000 m²)
    return round(area_m2 / 10000, 4)


def calculate_centroid(geojson_dict: dict) -> Centroid:
    """Calculate centroid of a geometry"""
    geom = shape(geojson_dict)
    centroid = geom.centroid
    return Centroid(
        latitude=round(centroid.y, 6),
        longitude=round(centroid.x, 6)
    )


def is_polygon_in_ocean(geojson_dict: dict) -> bool:
    """
    Simple check if polygon is likely in the ocean.
    For hackathon purposes, just check if centroid is in Mexico bounding box.
    """
    centroid = calculate_centroid(geojson_dict)
    
    # Rough bounding box for Mexico
    mexico_bounds = {
        "min_lat": 14.5,
        "max_lat": 32.7,
        "min_lon": -118.4,
        "max_lon": -86.7
    }
    
    is_in_mexico = (
        mexico_bounds["min_lat"] <= centroid.latitude <= mexico_bounds["max_lat"] and
        mexico_bounds["min_lon"] <= centroid.longitude <= mexico_bounds["max_lon"]
    )
    
    return not is_in_mexico


def simplify_geometry(geojson_dict: dict, tolerance: float = 0.0001) -> dict:
    """
    Simplify geometry to reduce vertex count.
    Useful for polygons with too many points (>5000 for TRACES NT limit).
    
    Tolerance is in degrees (~11m at equator for 0.0001)
    """
    geom = shape(geojson_dict)
    simplified = geom.simplify(tolerance, preserve_topology=True)
    return mapping(simplified)


def get_vertex_count(geojson_dict: dict) -> int:
    """Count total vertices in a geometry"""
    geom = shape(geojson_dict)
    
    if isinstance(geom, Polygon):
        return len(geom.exterior.coords)
    else:
        # MultiPolygon
        return sum(len(p.exterior.coords) for p in geom.geoms)
