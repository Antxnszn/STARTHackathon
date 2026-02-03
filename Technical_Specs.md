# **🥑 GreenPass Agro-Export: Technical Design Document (TDD)**

**Versión:** 1.0 (Hackathon MVP)

**Fecha:** Enero 2026

**Arquitectura:** Microservicios Modulares (The Triad Pattern)

## **1\. Visión Técnica**

El objetivo es construir una **Infraestructura de Datos Geoespaciales** que valide automáticamente el cumplimiento del reglamento EUDR (European Union Deforestation Regulation). El sistema ingesta polígonos geográficos, consulta APIs satelitales y climáticas, y emite un "Pasaporte Digital" (JSON) compatible con el sistema TRACES NT de la UE.

**Principios de Diseño:**

* **Decoupling:** Cada servicio puede fallar sin tumbar toda la app.  
* **Auditability:** Cada decisión del sistema (Aprobado/Rechazado) debe quedar registrada.  
* **Scalability:** Preparado para multi-tenancy (múltiples exportadores) y multi-commodity (aguacate hoy, café mañana).

## **2\. Stack Tecnológico**

### **Backend (Python / FastAPI)**

Elegimos **Python** por su dominio en librerías geoespaciales y **FastAPI** por su velocidad y generación automática de documentación (Swagger UI), vital para el demo.

* **Lenguaje:** Python 3.10+  
* **Framework:** FastAPI \+ Uvicorn  
* **Validación de Datos:** Pydantic (v2)  
* **Geo-Procesamiento:** geopandas, shapely, pyproj  
* **Cliente HTTP:** httpx (para consultas asíncronas a APIs externas)

### **Base de Datos & Almacenamiento**

* **Base de Datos Relacional:** PostgreSQL 15+  
* **Extensión Espacial (CRÍTICO):** **PostGIS** (Para guardar polígonos y hacer queries espaciales).  
* **Storage:** Google Storage (o simulación local MinIO / sistema de archivos) para guardar los GeoJSON crudos.

### **Infraestructura**

* **Contenerización:** Docker & Docker Compose (Entorno de desarrollo unificado).  
* **Despliegue:** Render.com o Railway (Soportan Dockerfile y PostGIS nativo).

## **3\. Arquitectura de Servicios (The Triad)**

Para el equipo de 3 Backends, dividiremos la lógica en tres dominios claros. Aunque en producción serían microservicios separados, para el hackathon pueden vivir en el mismo repo como "Módulos" o en 3 contenedores distintos orquestados por Docker Compose.

### **🏛️ Backend 1: Core Orchestrator & Compliance**

**Responsable:** *Lead Backend / Architect*

**Misión:** Gestión de usuarios, orquestación del flujo y generación del entregable final.

**Responsabilidades:**

1. **Auth & Tenant:** Manejo de JWT y separación lógica de datos por empresa (Avocados Mexico vs Del Monte).  
2. **Project State Machine:** Manejar estados: UPLOADED \-\> PROCESSING \-\> APPROVED / REJECTED.  
3. **File Management:** Recibir el .geojson del frontend y guardarlo seguro.  
4. **Integration Hub:** Llamar a los servicios de Geo y Env (Dev 2 y Dev 3), agregar sus respuestas y guardar en DB.  
5. **TRACES NT Engine:** Construir el JSON final con la estructura legal de la UE basada en los resultados.

**Endpoints Clave:**

* POST /api/projects: Crea proyecto.  
* POST /api/projects/{id}/upload: Recibe archivo.  
* GET /api/projects/{id}/report: Devuelve el JSON final de TRACES.

### **🛰️ Backend 2: Geo-Spatial Engine**

**Responsable:** *Geo Data Specialist*

**Misión:** Análisis geométrico y validación de deforestación.

**Responsabilidades:**

1. **Geometry Validation:** ¿El polígono está cerrado? ¿Se auto-intersecta? ¿Está en México? (Usa shapely).  
2. **Global Forest Watch (GFW) Integration:** Conectar con la API de GFW para buscar alertas GLAD/RADD.  
   * *Endpoint GFW:* /glad-alerts/download o consulta por Geostore.  
3. **Sentinel-2 Verification (Opcional/Simulado):** Validar si hay cobertura nubosa excesiva.

**Endpoints Clave:**

* POST /geo/analyze: Recibe GeoJSON \-\> Retorna { "is\_valid": true, "area\_ha": 14.2, "deforestation\_alerts": 0 }.

### **💧 Backend 3: Environmental Impact Engine**

**Responsable:** *Data Scientist / API Integrator*

**Misión:** Análisis de agua, clima y huella de carbono.

**Responsabilidades:**

1. **Water Risk (WRI Aqueduct):** Consultar API de Aqueduct para obtener el "Baseline Water Stress".  
2. **Local Compliance (CONAGUA/SINA):**  
   * *Hack:* Cargar un CSV/JSON estático con las coordenadas de acuíferos en veda de México y hacer una búsqueda de "Punto en Polígono" localmente.  
3. **Climate History (Open-Meteo):** Validar precipitación histórica vs requerimiento del cultivo.  
4. **Carbon Calculation (Climatiq):** Si hubo cambio de uso de suelo (reportado por Dev 2), calcular CO2e.

**Endpoints Clave:**

* POST /env/analyze: Recibe Centroide (Lat/Lon) \-\> Retorna { "water\_risk": "High", "aquifer\_veda": true, "carbon\_footprint": 50.5 }.

## **4\. Modelo de Datos (ERD \- PostgreSQL)**

```sql
-- Habilitar PostGIS  
CREATE EXTENSION postgis;

CREATE TABLE organizations (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    name VARCHAR(255),  
    eori\_number VARCHAR(50) \-- Identificador Aduanero UE  
);

CREATE TABLE projects (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    org\_id UUID REFERENCES organizations(id),  
    name VARCHAR(255),  
    status VARCHAR(50) DEFAULT 'PROCESSING', \-- PROCESSING, COMPLIANT, NON\_COMPLIANT  
    commodity\_code VARCHAR(20) DEFAULT '080440', \-- Aguacate  
    created\_at TIMESTAMP DEFAULT NOW()  
);

\-- Tabla Espacial (Manejada por Dev 2\)  
CREATE TABLE parcel\_geometries (  
    project\_id UUID REFERENCES projects(id),  
    geom GEOMETRY(POLYGON, 4326), \-- WGS84  
    area\_hectares FLOAT,  
    is\_valid BOOLEAN  
);

\-- Resultados de Auditoría (Llenada por Dev 2 y Dev 3\)  
CREATE TABLE audit\_results (  
    project\_id UUID REFERENCES projects(id),  
      
    \-- Forest Data  
    deforestation\_free BOOLEAN,  
    deforestation\_date DATE,  
      
    \-- Water Data  
    water\_risk\_score FLOAT, \-- 0.0 a 5.0 (WRI)  
    in\_veda\_zone BOOLEAN, \-- CONAGUA  
      
    \-- Carbon Data  
    estimated\_co2\_tonnes FLOAT,  
      
    audit\_date TIMESTAMP DEFAULT NOW()  
);
```

## **5\. Plan de Acción por Fases (48 Horas)**

### **Fase 1: Setup & Hello World (Horas 0-4)**

* **Todos:** Clonar repo, levantar Docker Compose con PostgreSQL \+ PostGIS.  
* **Acuerdo:** Definir los contratos de API (Estructura exacta de los JSON de entrada/salida entre servicios). *Si esto falla, la integración será un infierno.*

### **Fase 2: Desarrollo Independiente (Horas 4-20)**

* **Dev 1:** Crear Auth básica (hardcoded token ok para MVP) y el endpoint de Upload que guarda en disco/S3. Diseñar la estructura del JSON de TRACES.  
* **Dev 2:** Lograr que Python lea un GeoJSON y calcule su área con geopandas. Conectar con API GFW (o crear un mock si la API es lenta).  
* **Dev 3:** Scrapear/Descargar datos de CONAGUA a un CSV. Conectar con Open-Meteo y Climatiq.

### **Fase 3: La Gran Integración (Horas 20-30)**

* **Dev 1:** Conectar el orquestador. Cuando llega un archivo \-\> llamar a Dev 2 y Dev 3\.  
* **Backend:** Escribir la lógica de negocio:  
  * IF (deforestation \== True) OR (water\_risk \== 'Extreme') THEN Status \= 'NON\_COMPLIANT'  
* **DB:** Asegurar que los datos se guarden correctamente en las tablas audit\_results.

### **Fase 4: Generación de Valor & Frontend Mock (Horas 30-40)**

* **Dev 1:** Finalizar el generador de JSON para TRACES NT. Este es el "Deliverable" clave.  
* **Frontend (o Dev libre):** Conectar el React App a los endpoints reales (o dejarlos mockeados si falta tiempo, pero mostrando datos reales).

### **Fase 5: QA & Pitch Prep (Horas 40-48)**

* Probar casos de borde (¿Qué pasa si el polígono está en el océano?).  
* Preparar los datos de demostración (Un GeoJSON "Bueno" y uno "Malo").  
* Despliegue en Render/Railway.

## **6\. Diccionario de APIs Externas (Cheat Sheet)**

| Servicio | URL Base / Doc | Auth | Uso en GreenPass |
| :---- | :---- | :---- | :---- |
| **Global Forest Watch** | https://data-api.globalforestwatch.org | Open | Verificar alertas de deforestación (GLAD-L). |
| **WRI Aqueduct** | https://api.resourcewatch.org | Open | Obtener riesgo hídrico basal. |
| **Climatiq** | https://api.climatiq.io | API Key | Calcular CO2e por cambio de uso de suelo. |
| **Open-Meteo** | https://api.open-meteo.com/v1/forecast | Open | Datos históricos de lluvia/temperatura. |

## **7\. Escalabilidad (Para mencionar a los Jueces)**

1. **Colas Asíncronas (Future State):** "Actualmente el análisis es síncrono. Para producción, implementaremos **Celery \+ Redis**. El usuario sube el archivo, recibe un 'Job ID', y el sistema procesa los satélites en background".  
2. **Caché Geoespacial:** "Los datos de satélite no cambian cada segundo. Implementaremos caché de resultados basados en Geohash para no consultar GFW repetidamente por la misma zona".  
3. **Seguridad de Datos:** "Los polígonos son propiedad intelectual de los agricultores. En producción, la columna geom estará encriptada en reposo".

## **8\. Snippet: Docker Compose (Para empezar YA)**

Guarden esto como docker-compose.yml en la raíz para tener DB y PostGIS listo.

```yaml
version: '3.8'

services:  
  db:  
    image: postgis/postgis:15-3.3  
    environment:  
      POSTGRES\_USER: greenpass  
      POSTGRES\_PASSWORD: hackathon\_password  
      POSTGRES\_DB: greenpass\_db  
    ports:  
      \- "5432:5432"  
    volumes:  
      \- postgres\_data:/var/lib/postgresql/data

  \# Aquí irían sus servicios de API  
  \# api-core: ...  
  \# api-geo: ...

volumes:  
  postgres\_data:
```
