"""
Tests for Environmental Analysis
"""
import pytest
from src.env.clients.aqueduct_client import AqueductClient


def test_water_risk_check():
    """Test water risk check for Michoacán location"""
    client = AqueductClient()
    
    # Uruapan, Michoacán coordinates (avocado region)
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        client.get_water_risk(19.4123, -102.0482)
    )
    
    assert "overall_water_risk" in result
    assert "overall_water_risk_score" in result
    assert result["overall_water_risk_score"] >= 0
    assert result["overall_water_risk_score"] <= 5


def test_veda_zone_outside():
    """Test veda zone check for location outside veda"""
    client = AqueductClient()
    
    # Uruapan - should NOT be in veda zone
    result = client.check_veda_zone(19.4123, -102.0482)
    
    assert result["in_veda"] is False
    assert result["aquifer_name"] is None


def test_veda_zone_inside():
    """Test veda zone check for location inside veda"""
    client = AqueductClient()
    
    # Valle de México - should BE in veda zone
    result = client.check_veda_zone(19.4, -99.1)
    
    assert result["in_veda"] is True
    assert result["aquifer_name"] == "Valle de México"
