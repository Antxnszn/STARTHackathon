#!/usr/bin/env python3
"""
Script de debug para probar las APIs externas directamente.
Ejecutar: python scripts/debug_apis.py
"""
import asyncio
import json
import httpx
from pathlib import Path

# Colores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_json(data):
    print(json.dumps(data, indent=2, default=str)[:1000])


# Cargar geometría de prueba
def load_test_geometry(filename="chiapas.geojson"):
    path = Path(__file__).parent.parent / "mocks" / "inputs" / filename
    with open(path) as f:
        data = json.load(f)
    return data["features"][0]["geometry"]


async def test_gfw_api():
    """Test Global Forest Watch API"""
    print_header("🛰️ Testing Global Forest Watch API")
    
    base_url = "https://data-api.globalforestwatch.org"
    geometry = load_test_geometry()
    
    print(f"Geometry: {json.dumps(geometry)[:100]}...")
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        # Load API Key
        import os
        from dotenv import load_dotenv
        load_dotenv()
        gfw_api_key = os.getenv("GFW_API_KEY")
        
        headers = {"Content-Type": "application/json"}
        if gfw_api_key:
            headers["Authorization"] = f"Bearer {gfw_api_key}"
            print_success(f"Using GFW API Key: {gfw_api_key[:4]}...***")
        else:
            print_warning("No GFW_API_KEY found in .env - requests might fail")

        # Step 1: Create geostore
        print("\n📍 Step 1: Creating geostore...")
        try:
            response = await client.post(
                f"{base_url}/geostore",
                json={"geometry": geometry},
                headers=headers
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print_success("Geostore created!")
                print_json(data)
                
                geostore_id = data.get("data", {}).get("gfw_geostore_id")
                area_ha = data.get("data", {}).get("gfw_area__ha", 0)
                print(f"\n🗺️  Geostore ID: {geostore_id}")
                print(f"📏 Area: {area_ha:.2f} hectares")
                
                if geostore_id:
                    # Step 2: Query tree cover loss
                    print("\n🌲 Step 2: Querying tree cover loss (2021-2024)...")
                    sql = "SELECT SUM(area__ha) as total_loss_ha, umd_tree_cover_loss__year FROM data WHERE umd_tree_cover_loss__year >= 2021 GROUP BY umd_tree_cover_loss__year ORDER BY umd_tree_cover_loss__year"
                    
                    response2 = await client.get(
                        f"{base_url}/dataset/umd_tree_cover_loss/latest/query/json",
                        params={"sql": sql, "geostore_id": geostore_id},
                        headers=headers
                    )
                    print(f"Status: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        loss_data = response2.json()
                        print_success("Tree cover loss data received!")
                        print_json(loss_data)
                        
                        # Analyze results
                        records = loss_data.get("data", [])
                        if records:
                            total_loss = sum(r.get("total_loss_ha", 0) or 0 for r in records)
                            print(f"\n{'='*40}")
                            print(f"📊 DEFORESTATION ANALYSIS RESULT:")
                            print(f"   Total loss since 2021: {total_loss:.4f} ha")
                            if total_loss > 0:
                                print_error(f"   ⛔ NOT EUDR COMPLIANT - Deforestation detected!")
                            else:
                                print_success(f"   ✅ EUDR COMPLIANT - No deforestation!")
                            print(f"{'='*40}")
                        else:
                            print_success("No tree cover loss records found - area is clean!")
                    else:
                        print_error(f"Failed: {response2.text[:500]}")
            else:
                print_error(f"Failed to create geostore: {response.text[:500]}")
                
        except Exception as e:
            print_error(f"GFW API Error: {type(e).__name__}: {e}")


async def test_openmeteo_api():
    """Test Open-Meteo Historical Weather API"""
    print_header("🌧️ Testing Open-Meteo Historical Weather API")
    
    # Coordenadas de Chiapas
    lat, lon = 19.154, -89.598
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2023-01-01",
        "end_date": "2023-01-07",  # Solo 7 días para test
        "daily": "precipitation_sum,temperature_2m_mean",
        "timezone": "America/Mexico_City"
    }
    
    print(f"Location: {lat}, {lon}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            print(f"\nStatus: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print_success("Weather data received!")
                print_json(data)
            else:
                print_error(f"Failed: {response.text[:500]}")
                
        except Exception as e:
            print_error(f"Open-Meteo Error: {type(e).__name__}: {e}")


async def test_climatiq_api():
    """Test Climatiq Carbon Emissions API"""
    print_header("🌿 Testing Climatiq Carbon API")
    
    # Cargar API key del .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("CLIMATIQ_API_KEY", "")
    
    if not api_key or api_key == "your_climatiq_api_key_here":
        print_warning("CLIMATIQ_API_KEY not configured in .env")
        print("To test, get a free API key from: https://www.climatiq.io/")
        return
    
    url = "https://api.climatiq.io/data/v1/estimate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "emission_factor": {
            "activity_id": "land_use_change-forests-type_tropical_rainforest",
            "data_version": "^21"
        },
        "parameters": {
            "area": 10.0,
            "area_unit": "ha"
        }
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            print(f"\nStatus: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print_success("Carbon estimate received!")
                print_json(data)
            else:
                print_error(f"Failed: {response.text[:500]}")
                
        except Exception as e:
            print_error(f"Climatiq Error: {type(e).__name__}: {e}")


async def main():
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════╗")
    print(f"║       GreenPass API Debug Tool                           ║")
    print(f"╚══════════════════════════════════════════════════════════╝{RESET}")
    
    await test_gfw_api()
    await test_openmeteo_api()
    await test_climatiq_api()
    
    print_header("Debug Complete")


if __name__ == "__main__":
    asyncio.run(main())
