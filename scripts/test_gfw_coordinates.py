#!/usr/bin/env python3
"""
Script de prueba para analizar coordenadas específicas con GFW.
Ejecutar: python scripts/test_gfw_coordinates.py
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.geometry import calculate_centroid, calculate_area_hectares
import httpx

# Implementación simplificada de AqueductClient (sin dependencias de settings)
WATER_STRESS_ZONES = {
    "michoacan_alta": {
        "lat_range": (19.0, 20.0),
        "lon_range": (-103.0, -101.5),
        "risk_level": "Low-Medium",
        "risk_score": 1.5,
    },
    "jalisco": {
        "lat_range": (19.5, 21.5),
        "lon_range": (-105.0, -102.5),
        "risk_level": "Medium",
        "risk_score": 2.0,
    },
    "edomex": {
        "lat_range": (18.8, 20.2),
        "lon_range": (-100.5, -98.5),
        "risk_level": "Medium-High",
        "risk_score": 3.0,
    },
}

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

def get_water_risk(lat: float, lon: float):
    """Get water risk assessment for a location (simplified version)"""
    for zone_name, zone in WATER_STRESS_ZONES.items():
        if (zone["lat_range"][0] <= lat <= zone["lat_range"][1] and
            zone["lon_range"][0] <= lon <= zone["lon_range"][1]):
            score = zone["risk_score"]
            return {
                "latitude": lat,
                "longitude": lon,
                "zone": zone_name,
                "baseline_water_stress": _score_to_stress(score),
                "baseline_water_stress_score": score,
                "water_depletion": "Low (<5%)",
                "water_depletion_score": 0.8,
                "interannual_variability": "Medium (0.5-0.75)",
                "interannual_variability_score": 0.6,
                "overall_water_risk": zone["risk_level"],
                "overall_water_risk_score": score,
            }
    
    # Default
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

def check_veda_zone(lat: float, lon: float):
    """Check if location is in a CONAGUA veda zone"""
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

def _score_to_stress(score: float) -> str:
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

# Cargar variables de entorno
load_dotenv()

# Configuración directa (sin usar settings)
GFW_API_URL = os.getenv("GFW_API_URL", "https://data-api.globalforestwatch.org")
GFW_API_KEY = os.getenv("GFW_API_KEY", "")

# Colores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{CYAN}ℹ️  {text}{RESET}")

def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def create_polygon_from_coordinates(coords):
    """
    Crea un polígono GeoJSON a partir de coordenadas [lat, lng].
    
    Nota: GeoJSON usa [longitude, latitude], así que invertimos el orden.
    """
    # Convertir [lat, lng] a [lng, lat] para GeoJSON
    geo_coords = [[coord["lng"], coord["lat"]] for coord in coords]
    
    # Asegurar que el polígono esté cerrado (último punto igual al primero)
    if geo_coords[0] != geo_coords[-1]:
        geo_coords.append(geo_coords[0])
    
    polygon = {
        "type": "Polygon",
        "coordinates": [geo_coords]
    }
    
    return polygon


async def analyze_coordinates():
    """Analiza las coordenadas proporcionadas con GFW"""
    
    # Coordenadas proporcionadas por el usuario
    coordinates = [
        {"lat": 19.52326975620081, "lng": -101.85579299926759},
        {"lat": 19.520155233059555, "lng": -101.86338901519777},
        {"lat": 19.514735010718574, "lng": -101.85373306274415},
        {"lat": 19.519508051887833, "lng": -101.84875488281251},
        {"lat": 19.52326975620081, "lng": -101.85579299926759}  # Cierra el polígono
    ]
    
    print_header("🌍 Análisis de Coordenadas con GFW")
    
    # Crear polígono GeoJSON
    print_info("Creando polígono GeoJSON a partir de las coordenadas...")
    geometry = create_polygon_from_coordinates(coordinates)
    
    print("\n📍 Coordenadas del polígono:")
    for i, coord in enumerate(coordinates[:-1]):  # No mostrar el último que es duplicado
        print(f"   Punto {i}: Lat {coord['lat']:.10f}, Lng {coord['lng']:.10f}")
    
    print(f"\n📐 Polígono GeoJSON:")
    print_json(geometry)
    
    # Calcular centroide
    print("\n" + "="*60)
    print_info("Calculando centroide del polígono...")
    try:
        from src.shared.geometry import calculate_centroid
        centroid = calculate_centroid(geometry)
        print_success(f"Centroide calculado:")
        print(f"   Latitud:  {centroid.latitude:.10f}")
        print(f"   Longitud: {centroid.longitude:.10f}")
    except Exception as e:
        print_error(f"Error calculando centroide: {e}")
        return
    
    # Calcular área
    try:
        area_ha = calculate_area_hectares(geometry)
        print_success(f"Área del polígono: {area_ha:.4f} hectáreas")
    except Exception as e:
        print_error(f"Error calculando área: {e}")
    
    # Análisis con GFW
    print("\n" + "="*60)
    print_info("Iniciando análisis con Global Forest Watch API...")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if GFW_API_KEY:
        headers["x-api-key"] = GFW_API_KEY
        print_info(f"Usando API Key: {GFW_API_KEY[:4]}...***")
    else:
        print_info("No se encontró GFW_API_KEY - intentando sin autenticación")
    
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Crear geostore
            print("\n📍 Paso 1: Creando geostore en GFW...")
            geostore_response = await client.post(
                f"{GFW_API_URL}/geostore",
                json={"geometry": geometry},
                headers=headers
            )
            
            geostore_response.raise_for_status()
            geostore_data = geostore_response.json().get("data", {})
            
            if not geostore_data:
                print_error("No se pudo crear el geostore")
                print("Respuesta completa:")
                print_json(geostore_response.json())
                return
            
            geostore_id = geostore_data.get("gfw_geostore_id")
            gfw_area_ha = geostore_data.get("gfw_area__ha", 0)
            
            if not geostore_id:
                print_error("No se obtuvo geostore_id de la respuesta")
                print("Respuesta completa:")
                print_json(geostore_data)
                return
            
            print_success(f"Geostore creado exitosamente!")
            print(f"   Geostore ID: {geostore_id}")
            print(f"   Área (GFW): {gfw_area_ha:.4f} hectáreas")
            
            # Consultar pérdida de cobertura arbórea
            print("\n🌲 Paso 2: Consultando pérdida de cobertura arbórea (2021-2024)...")
            sql = """
                SELECT 
                    SUM(area__ha) as total_loss_ha,
                    umd_tree_cover_loss__year
                FROM data
                WHERE umd_tree_cover_loss__year >= 2021
                  AND umd_tree_cover_loss__year <= 2024
                GROUP BY umd_tree_cover_loss__year
                ORDER BY umd_tree_cover_loss__year
            """
            
            loss_response = await client.get(
                f"{GFW_API_URL}/dataset/umd_tree_cover_loss/latest/query/json",
                params={
                    "sql": sql.strip().replace("\n", " "),
                    "geostore_id": geostore_id
                },
                headers=headers
            )
            
            loss_response.raise_for_status()
            loss_data = loss_response.json()
            
            print_success("Datos de pérdida de cobertura recibidos!")
            print("\n📊 Resultados del análisis:")
            print_json(loss_data)
            
            # Analizar resultados
            records = loss_data.get("data", [])
            if records:
                print("\n" + "="*60)
                print(f"{BLUE}📊 ANÁLISIS DE DEFORESTACIÓN:{RESET}")
                print("="*60)
                
                total_loss = 0
                for record in records:
                    year = record.get("umd_tree_cover_loss__year")
                    loss_ha = record.get("total_loss_ha", 0) or 0
                    total_loss += loss_ha
                    if loss_ha > 0:
                        print(f"   {year}: {loss_ha:.4f} ha de pérdida")
                    else:
                        print(f"   {year}: Sin pérdida detectada")
                
                print(f"\n   Total pérdida (2021-2024): {total_loss:.4f} ha")
                
                if total_loss > 0:
                    print_error(f"   ⛔ DEFORESTACIÓN DETECTADA - No cumple EUDR")
                else:
                    print_success(f"   ✅ SIN DEFORESTACIÓN - Cumple EUDR")
                
                print("="*60)
            else:
                print_success("\n✅ No se encontraron registros de pérdida de cobertura arbórea")
                print("   El área está libre de deforestación según GFW")
            
            # Consultar alertas GLAD
            print("\n\n🔔 Paso 3: Consultando alertas GLAD...")
            try:
                glad_sql = "SELECT COUNT(*) as alert_count, SUM(area__ha) as total_area_ha FROM data"
                
                glad_response = await client.get(
                    f"{GFW_API_URL}/dataset/umd_glad_landsat_alerts/latest/query/json",
                    params={"sql": glad_sql, "geostore_id": geostore_id},
                    headers=headers
                )
                
                glad_response.raise_for_status()
                glad_data = glad_response.json()
                
                print_success("Datos de alertas GLAD recibidos!")
                print_json(glad_data)
                
                alert_count = glad_data.get("data", [{}])[0].get("alert_count", 0) if glad_data.get("data") else 0
                alert_area = glad_data.get("data", [{}])[0].get("total_area_ha", 0) if glad_data.get("data") else 0
                
                if alert_count > 0:
                    print(f"\n⚠️  Alertas GLAD detectadas: {alert_count}")
                    print(f"   Área afectada: {alert_area:.4f} ha")
                else:
                    print_success("✅ No se detectaron alertas GLAD")
                    
            except Exception as e:
                print_error(f"Error consultando alertas GLAD: {e}")
                import traceback
                traceback.print_exc()
        
    except httpx.HTTPStatusError as e:
        print_error(f"Error HTTP en análisis GFW: {e.response.status_code}")
        print(f"Respuesta: {e.response.text[:500]}")
    except Exception as e:
        print_error(f"Error en análisis GFW: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Análisis de Water Stress
    print("\n\n" + "="*60)
    print_info("Iniciando análisis de Water Stress (Aqueduct)...")
    
    try:
        # Obtener análisis de water risk usando el centroide
        print(f"\n💧 Analizando water stress para el centroide...")
        print(f"   Latitud: {centroid.latitude:.10f}")
        print(f"   Longitud: {centroid.longitude:.10f}")
        
        water_risk = get_water_risk(
            centroid.latitude,
            centroid.longitude
        )
        
        print_success("Datos de water stress recibidos!")
        print("\n📊 Resultados del análisis de Water Stress:")
        print_json(water_risk)
        
        # Verificar zona de veda
        print("\n🔍 Verificando si está en zona de veda (CONAGUA)...")
        veda_check = check_veda_zone(
            centroid.latitude,
            centroid.longitude
        )
        
        print_json(veda_check)
        
        # Resumen del análisis
        print("\n" + "="*60)
        print(f"{BLUE}💧 ANÁLISIS DE WATER STRESS:{RESET}")
        print("="*60)
        print(f"   Zona identificada: {water_risk.get('zone', 'N/A')}")
        print(f"   Baseline Water Stress: {water_risk.get('baseline_water_stress', 'N/A')}")
        print(f"   Water Stress Score: {water_risk.get('baseline_water_stress_score', 0):.2f}")
        print(f"   Water Depletion: {water_risk.get('water_depletion', 'N/A')}")
        print(f"   Interannual Variability: {water_risk.get('interannual_variability', 'N/A')}")
        print(f"   Overall Water Risk: {water_risk.get('overall_water_risk', 'N/A')}")
        print(f"   Overall Risk Score: {water_risk.get('overall_water_risk_score', 0):.2f}")
        
        if veda_check.get('in_veda', False):
            print(f"\n   ⚠️  ZONA DE VEDA DETECTADA:")
            print(f"      Acuífero: {veda_check.get('aquifer_name', 'N/A')}")
            print(f"      Restricción: {veda_check.get('restriction_type', 'N/A')}")
        else:
            print_success("\n   ✅ No está en zona de veda")
        
        print("="*60)
        
    except Exception as e:
        print_error(f"Error en análisis de Water Stress: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(analyze_coordinates())
