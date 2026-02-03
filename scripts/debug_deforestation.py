#!/usr/bin/env python3
"""
Script para depurar el problema de detección de deforestación
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geo.service import GeoService
from src.geo.schemas.requests import GeoAnalysisRequest

async def test_deforestation():
    """Probar la detección de deforestación con el archivo michoacan.geojson"""
    
    # Cargar el archivo GeoJSON
    geojson_path = Path(__file__).parent.parent / "mocks" / "inputs" / "michoacan.geojson"
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    
    print("="*60)
    print("Probando detección de deforestación")
    print("="*60)
    print(f"\nArchivo: {geojson_path}")
    print(f"Tipo: {geojson_data.get('type')}")
    
    # Crear el servicio
    geo_service = GeoService()
    
    # Crear request
    request = GeoAnalysisRequest(
        project_id="test-debug",
        geometry=geojson_data,
        cutoff_date=date(2020, 12, 31)
    )
    
    print("\nEjecutando análisis...")
    try:
        result = await geo_service.analyze(request)
        
        print("\n" + "="*60)
        print("RESULTADOS:")
        print("="*60)
        print(f"Área: {result.area_hectares} ha")
        print(f"Centroide: {result.centroid.latitude}, {result.centroid.longitude}")
        print(f"\nDeforestación:")
        print(f"  is_deforestation_free: {result.deforestation_analysis.is_deforestation_free}")
        print(f"  alerts_count: {result.deforestation_analysis.alerts_count}")
        print(f"  total_loss_ha_post_cutoff: {result.deforestation_analysis.total_loss_ha_post_cutoff}")
        print(f"  Periodo: {result.deforestation_analysis.analysis_period.start} a {result.deforestation_analysis.analysis_period.end}")
        
        if result.deforestation_analysis.is_deforestation_free:
            print("\n❌ PROBLEMA: Está marcando como libre de deforestación cuando NO debería!")
        else:
            print("\n✅ Correcto: Detectó deforestación")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deforestation())
