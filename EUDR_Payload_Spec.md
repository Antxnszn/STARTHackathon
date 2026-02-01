# **🇪🇺 EUDR / TRACES NT: Especificación de Intercambio de Datos (DDS)**

**Proyecto:** GreenPass

**Módulo:** Core Orchestrator (Backend 1\)

**Estándar:** Reglamento (UE) 2023/1115 (EUDR) \- Anexo II

**Formato de Salida:** JSON (Compatible con REST API v2 de TRACES NT)

## **1\. Introducción**

Este documento define la estructura de datos, reglas de validación y formato del **Due Diligence Statement (DDS)**. Este archivo JSON es el artefacto final que genera GreenPass para permitir la entrada de mercancías a la Unión Europea.

El objetivo es garantizar la interoperabilidad con el sistema **TRACES NT** (Trade Control and Expert System New Technology) y evitar rechazos automáticos en aduana por errores de formato o geometría.

## **2\. Estructura del JSON (The Payload)**

El payload se divide en 4 bloques lógicos: **Cabecera (Operador)**, **Mercancía**, **Geolocalización** y **Declaración**.

### **Bloque A: Información del Operador**

Identifica a la entidad legal responsable de la exportación.

| Campo JSON | Tipo | Descripción | Regla de Negocio |
| :---- | :---- | :---- | :---- |
| operator\_ref\_id | String | ID interno del sistema (UUID). | Único por declaración. |
| operator\_eori | String | Número de Registro e Identificación de Operadores Económicos. | Formato MX \+ 10-15 dígitos. Obligatorio. |
| importer\_name | String | Nombre de la empresa importadora en la UE. | Debe coincidir con el registro en TRACES. |
| certificate\_reference | String | Número de referencia de GreenPass. | Formato: GP-{YYYY}-{SEQ}. |

### **Bloque B: Datos de la Mercancía (Commodity)**

Describe el producto físico.

| Campo JSON | Tipo | Descripción | Regla de Negocio |
| :---- | :---- | :---- | :---- |
| hs\_code | String | Código del Sistema Armonizado. | **080440** (Aguacates frescos o secos). |
| description | String | Descripción en texto libre. | Ej: "Fresh Avocado Hass \- Grade A". |
| net\_mass\_kg | Float | Peso neto en Kilogramos. | \> 0\. Precisión 2 decimales. |
| country\_of\_production | String | Código ISO 3166-1 alpha-2. | Debe ser **"MX"**. |

### **Bloque C: Geolocalización (CRÍTICO)**

Este es el bloque más sensible a errores. Define de dónde viene el producto.

| Campo JSON | Tipo | Descripción | Regla de Negocio |
| :---- | :---- | :---- | :---- |
| geo\_type | String | Tipo de geometría. | "POINT" (\<4 ha) o "POLYGON" (\>4 ha). |
| coordinates | Array | Lista de latitud/longitud. | Formato WGS84 (EPSG:4326). |
| area\_hectares | Float | Tamaño de la parcela. | Calculado automáticamente por Backend 2\. |

### **Bloque D: Declaración de Cumplimiento**

La parte legal donde GreenPass certifica la validez.

| Campo JSON | Tipo | Descripción | Regla de Negocio |
| :---- | :---- | :---- | :---- |
| deforestation\_free | Boolean | ¿Libre de deforestación \> 2020? | Debe ser true. Si es false, no se genera el JSON. |
| legality\_verified | Boolean | ¿Cumple leyes locales (Agua)? | Debe ser true. |
| risk\_assessment\_ref | String | Hash del reporte de auditoría GreenPass. | Enlace inmutable al log de auditoría. |

## **3\. Ejemplo de Payload Completo (JSON)**

Este es el JSON exacto que generará el endpoint GET /api/projects/{id}/report.

{  
  "submission\_type": "DDS\_IMPORT",  
  "version": "2.1",  
  "header": {  
    "reference\_number": "GP-2025-MX-88291",  
    "operator": {  
      "name": "Avocados From Mexico S.A.",  
      "eori": "MX123456789012",  
      "address": "Av. Francisco Medina Ascencio 123, Uruapan, MX"  
    },  
    "destination\_market": "NL" // Países Bajos  
  },  
  "commodity": {  
    "hs\_code": "08044000",  
    "scientific\_name": "Persea americana",  
    "trade\_name": "Hass Avocado",  
    "quantity": {  
      "amount": 18500.50,  
      "unit": "KGM" // Kilogramos  
    }  
  },  
  "geolocation": {  
    "type": "FeatureCollection",  
    "features": \[  
      {  
        "type": "Feature",  
        "properties": {  
          "plot\_id": "LOTE-892-A"  
        },  
        "geometry": {  
          "type": "Polygon",  
          "coordinates": \[  
            \[  
              \[-102.048215, 19.412301\],  
              \[-102.049100, 19.412550\],  
              \[-102.048850, 19.411020\],  
              \[-102.048215, 19.412301\]   
            \]  
          \]  
        }  
      }  
    \]  
  },  
  "compliance": {  
    "deforestation\_free\_post\_2020": true,  
    "relevant\_legislation\_check": true,  
    "audit\_metadata": {  
      "engine": "GreenPass v1.0",  
      "verification\_timestamp": "2025-10-25T14:30:00Z",  
      "water\_risk\_assessment": "APPROVED\_CONDITIONAL"  
    }  
  }  
}

## **4\. Reglas de Validación Técnica (Cómo evitar rechazos)**

Para que el backend no falle, deben implementarse estas validaciones en **Pydantic** antes de generar el JSON:

### **1\. Regla del Polígono Cerrado**

* **Error Común:** El primer punto y el último punto de la lista de coordenadas no son idénticos.  
* **Solución:** Backend 2 debe forzar el cierre del polígono:  
  if coordinates\[0\] \!= coordinates\[-1\]: coordinates.append(coordinates\[0\])

### **2\. Regla de Precisión (6 Decimales)**

* **Error Común:** Enviar coordenadas con demasiados decimales (ej. 19.41230129384) infla el tamaño del archivo innecesariamente.  
* **Solución:** Truncar a 6 decimales (aprox. 11 cm de precisión), suficiente para EUDR.

### **3\. Regla "Anti-Bowtie" (Auto-Intersección)**

* **Error Común:** Las líneas del polígono se cruzan entre sí (forma de moño), lo cual es geométricamente inválido.  
* **Solución:** Usar shapely.validation.make\_valid() en Backend 2 para corregir la geometría antes de guardarla.

### **4\. Regla del Límite de Puntos**

* **Restricción:** TRACES NT a veces rechaza polígonos con \> 5,000 vértices por complejidad de procesamiento.  
* **Solución:** Si len(coordinates) \> 5000, aplicar algoritmo de simplificación (Douglas-Peucker) con tolerancia mínima.

## **5\. Implementación en Python (Snippet para Backend 1\)**

Usa este modelo Pydantic para asegurar que el JSON siempre salga perfecto.

from pydantic import BaseModel, Field, field\_validator  
from typing import List, Literal

class Operator(BaseModel):  
    name: str  
    eori: str \= Field(..., pattern=r"^\[A-Z\]{2}\[0-9A-Z\]{1,15}$")

class Geometry(BaseModel):  
    type: Literal\["Polygon", "Point"\]  
    coordinates: List\[List\[List\[float\]\]\] \# Para Polygon

    @field\_validator('coordinates')  
    def check\_closed\_polygon(cls, v):  
        \# Valida que el primer y último punto sean iguales  
        if v\[0\]\[0\] \!= v\[0\]\[-1\]:  
            raise ValueError("Polygon must be closed")  
        return v

class EUDRPayload(BaseModel):  
    submission\_type: str \= "DDS\_IMPORT"  
    header: dict  
    geolocation: Geometry  
    \# ... resto de campos  
