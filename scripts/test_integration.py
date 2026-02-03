#!/usr/bin/env python3
"""
Script de prueba de integración end-to-end
Prueba el flujo completo: crear proyecto -> subir geometría -> analizar -> generar reporte
"""
import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.service import CoreService
from src.core.schemas.requests import ProjectCreate


async def test_integration():
    """Test end-to-end integration"""
    print("=" * 60)
    print("🧪 Testing GreenPass Integration")
    print("=" * 60)
    
    service = CoreService()
    
    # Step 1: Create project
    print("\n1️⃣ Creating project...")
    project_data = ProjectCreate(
        name="Test Huerta - Chiapas",
        organization_name="Test Exporters S.A.",
        organization_eori="MX123456789012",
        commodity_code="08044000",
        destination_market="NL"
    )
    project = await service.create_project(project_data)
    project_id = project.id
    print(f"✅ Project created: {project_id}")
    print(f"   Name: {project.name}")
    print(f"   Status: {project.status}")
    
    # Step 2: Load and upload geometry
    print("\n2️⃣ Uploading geometry...")
    geojson_path = Path(__file__).parent.parent / "mocks" / "inputs" / "chiapas.geojson"
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    
    await service.upload_geometry(project_id, geojson_data)
    print("✅ Geometry uploaded")
    
    # Step 3: Run analysis
    print("\n3️⃣ Running EUDR compliance analysis...")
    print("   (This may take 30-60 seconds due to API calls)")
    result = await service.run_analysis(project_id)
    
    print(f"\n✅ Analysis complete!")
    print(f"   Status: {result.status}")
    print(f"   Area: {result.area_hectares:.2f} hectares")
    print(f"   Geometry Valid: {result.geometry_valid}")
    print(f"\n   Deforestation:")
    print(f"     - Free: {result.deforestation.is_deforestation_free}")
    print(f"     - Alerts: {result.deforestation.alerts_count}")
    print(f"     - Loss: {result.deforestation.total_loss_ha_post_cutoff:.2f} ha")
    print(f"\n   Water Risk:")
    print(f"     - Level: {result.water.risk_level}")
    print(f"     - Score: {result.water.risk_score:.1f}")
    print(f"     - Veda Zone: {result.water.in_veda_zone}")
    print(f"\n   Climate:")
    print(f"     - Precipitation: {result.climate.avg_annual_precipitation_mm:.1f} mm")
    print(f"     - Temperature: {result.climate.avg_temperature_celsius:.1f}°C")
    print(f"     - Suitable: {result.climate.precipitation_suitable}")
    print(f"\n   Carbon:")
    print(f"     - CO2e: {result.carbon.estimated_co2e_tonnes:.2f} tonnes")
    print(f"     - Reason: {result.carbon.reason}")
    
    print(f"\n   Summary: {result.compliance_summary}")
    
    # Step 4: Generate report (if compliant)
    if result.status == "COMPLIANT":
        print("\n4️⃣ Generating EUDR report...")
        report = await service.generate_eudr_report(project_id)
        if report:
            print(f"✅ Report generated!")
            print(f"   Reference: {report.greenpass_reference}")
            print(f"   Submission Type: {report.submission_type}")
            print(f"   Version: {report.version}")
        else:
            print("❌ Failed to generate report")
    else:
        print("\n4️⃣ Skipping report generation (project not compliant)")
    
    print("\n" + "=" * 60)
    print("✅ Integration test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_integration())
