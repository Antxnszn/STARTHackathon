"""
GeoJSON Pydantic Models - Shared across all modules
"""
from typing import List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator


class Centroid(BaseModel):
    """Geographic centroid point"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class PointGeometry(BaseModel):
    """GeoJSON Point geometry"""
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=3)
    
    @property
    def longitude(self) -> float:
        return self.coordinates[0]
    
    @property
    def latitude(self) -> float:
        return self.coordinates[1]


class PolygonGeometry(BaseModel):
    """GeoJSON Polygon geometry"""
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]]
    
    @field_validator('coordinates')
    @classmethod
    def validate_closed_polygon(cls, v):
        """Ensure polygon is closed (first point == last point)"""
        if v and v[0]:
            ring = v[0]
            if len(ring) < 4:
                raise ValueError("Polygon must have at least 4 coordinates (3 points + closing)")
            if ring[0] != ring[-1]:
                # Auto-close the polygon
                v[0] = ring + [ring[0]]
        return v
    
    @field_validator('coordinates')
    @classmethod
    def round_coordinates(cls, v):
        """Round coordinates to 6 decimal places (11cm precision)"""
        def round_coord(coord):
            return [round(c, 6) for c in coord]
        
        return [[round_coord(point) for point in ring] for ring in v]


class MultiPolygonGeometry(BaseModel):
    """GeoJSON MultiPolygon geometry"""
    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: List[List[List[List[float]]]]


# Union type for any geometry
Geometry = Union[PointGeometry, PolygonGeometry, MultiPolygonGeometry]


class Feature(BaseModel):
    """GeoJSON Feature"""
    type: Literal["Feature"] = "Feature"
    properties: dict = Field(default_factory=dict)
    geometry: Geometry


class FeatureCollection(BaseModel):
    """GeoJSON FeatureCollection"""
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[Feature]


class GeoJSONInput(BaseModel):
    """
    Flexible GeoJSON input that accepts either:
    - A raw Polygon/MultiPolygon geometry
    - A Feature
    - A FeatureCollection
    """
    geojson: Union[Geometry, Feature, FeatureCollection]
    
    def get_geometry(self) -> Geometry:
        """Extract the primary geometry from the input"""
        if isinstance(self.geojson, (PolygonGeometry, PointGeometry, MultiPolygonGeometry)):
            return self.geojson
        elif isinstance(self.geojson, Feature):
            return self.geojson.geometry
        elif isinstance(self.geojson, FeatureCollection):
            if self.geojson.features:
                return self.geojson.features[0].geometry
            raise ValueError("FeatureCollection is empty")
        raise ValueError("Cannot extract geometry from input")
