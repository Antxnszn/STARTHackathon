"""
WRI Aqueduct Water Risk Client (Mock Implementation)

For hackathon: Uses mock data based on Mexican aquifer zones.
Production would use WRI Aqueduct API or downloaded dataset.

Real API: https://www.wri.org/aqueduct
"""
import json
from pathlib import Path
from typing import Dict, Any

from src.config import settings


# Mexican states with known water stress issues
WATER_STRESS_ZONES = {
    # High stress (aguacate regions in Michoacán have varied conditions)
    "michoacan_alta": {
        "lat_range": (19.0, 20.0),
        "lon_range": (-103.0, -101.5),
        "risk_level": "Low-Medium",
        "risk_score": 1.5,
    },
    # Jalisco
    "jalisco": {
        "lat_range": (19.5, 21.5),
        "lon_range": (-105.0, -102.5),
        "risk_level": "Medium",
        "risk_score": 2.0,
    },
    # Estado de México - higher stress
    "edomex": {
        "lat_range": (18.8, 20.2),
        "lon_range": (-100.5, -98.5),
        "risk_level": "Medium-High",
        "risk_score": 3.0,
    },
}

# CONAGUA Veda zones (aquifers with extraction restrictions)
# Simplified - in production would load from official CONAGUA data
VEDA_ZONES = [
    {
        "name": "Valle de México",
        "lat_range": (19.2, 19.6),
        "lon_range": (-99.4, -98.8),
    },
    {
        "name": "Laguna de Cuitzeo",
        "lat_range": (19.8, 20.1),
        "lon_range": (-101.2, -100.7),
    },
]


class AqueductClient:
    """
    Client for WRI Aqueduct Water Risk data.
    
    For hackathon: Uses mock data based on location.
    Production: Would integrate with WRI Aqueduct API or GeoJSON dataset.
    """
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
    
    async def get_water_risk(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get water risk assessment for a location.
        
        Returns risk levels for baseline water stress, water depletion,
        and overall water risk.
        """
        # Find matching zone
        for zone_name, zone in WATER_STRESS_ZONES.items():
            if (zone["lat_range"][0] <= lat <= zone["lat_range"][1] and
                zone["lon_range"][0] <= lon <= zone["lon_range"][1]):
                return {
                    "latitude": lat,
                    "longitude": lon,
                    "zone": zone_name,
                    "baseline_water_stress": self._score_to_stress(zone["risk_score"]),
                    "baseline_water_stress_score": zone["risk_score"],
                    "water_depletion": "Low (<5%)",
                    "water_depletion_score": 0.8,
                    "interannual_variability": "Medium (0.5-0.75)",
                    "interannual_variability_score": 0.6,
                    "overall_water_risk": zone["risk_level"],
                    "overall_water_risk_score": zone["risk_score"],
                }
        
        # Default to low-medium risk for unmatched locations in Mexico
        return {
            "latitude": lat,
            "longitude": lon,
            "zone": "default_mexico",
            "baseline_water_stress": "Low (<10%)",
            "baseline_water_stress_score": 1.0,
            "water_depletion": "Low (<5%)",
            "water_depletion_score": 0.5,
            "interannual_variability": "Low (<0.5)",
            "interannual_variability_score": 0.4,
            "overall_water_risk": "Low-Medium",
            "overall_water_risk_score": 1.2,
        }
    
    def check_veda_zone(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Check if location is in a CONAGUA veda (restricted) zone.
        
        Veda zones have restrictions on groundwater extraction.
        """
        for zone in VEDA_ZONES:
            if (zone["lat_range"][0] <= lat <= zone["lat_range"][1] and
                zone["lon_range"][0] <= lon <= zone["lon_range"][1]):
                return {
                    "in_veda": True,
                    "aquifer_name": zone["name"],
                    "restriction_type": "Extraction prohibited without permit",
                }
        
        return {
            "in_veda": False,
            "aquifer_name": None,
            "restriction_type": None,
        }
    
    def _score_to_stress(self, score: float) -> str:
        """Convert numeric score to stress category"""
        if score < 1:
            return "Low (<10%)"
        elif score < 2:
            return "Low-Medium (10-20%)"
        elif score < 3:
            return "Medium-High (20-40%)"
        elif score < 4:
            return "High (40-80%)"
        else:
            return "Extremely High (>80%)"
