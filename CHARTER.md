# Project Charter: GreenPass Agro-Export (RtSH 2026)

**Infraestructura de Datos para la Verificación Climática y Continuidad Comercial**

## 1. Resumen Ejecutivo

El sector aguacatero mexicano, con un valor de exportación superior a los $4,000 millones de USD, enfrenta una amenaza existencial debido a la entrada en vigor del **Reglamento de Deforestación de la Unión Europea (EUDR)** el 30 de diciembre de 2026. **GreenPass** es una plataforma SaaS de "Compliance-as-a-Service" que automatiza la debida diligencia ambiental. Transformamos datos satelitales y climáticos complejos en "Pasaportes Digitales" de exportación, asegurando que cada envío cumpla con las normativas de cero deforestación y gestión hídrica, protegiendo así la cuota de mercado de México frente a competidores con mayor madurez digital.

---

## 2. Alineación con el Reto "RtSH Mexico City 2026"

Nuestra solución es **Híbrida**, abordando simultáneamente los dos casos planteados por el hackathon para maximizar el impacto:

### A. Alineación con Caso A: Emisiones, MRV y Accountability

* 
**El Problema:** El reto identifica la "dificultad para verificar o comparar datos reportados" y la necesidad de mecanismos de "rendición de cuentas".


* **Nuestra Solución:** GreenPass actúa como un auditor digital imparcial. No confiamos en reportes manuales; verificamos la realidad del terreno mediante satélites. Convertimos la actividad de uso de suelo en datos verificables, cumpliendo con el objetivo de "transformar datos... en mecanismos de rendición de cuentas".



### B. Alineación con Caso B: Agua, Sequía y Prevención

* 
**El Problema:** El reto busca "priorizar intervenciones preventivas" y "anticipar riesgos" hídricos.


* **Nuestra Solución:** Integramos datos de estrés hídrico para bloquear preventivamente la certificación de cultivos en zonas de veda o sequía extrema, desincentivando la expansión agrícola en áreas vulnerables.

---

## 3. Definición del Problema y Urgencia (The Crisis)

### La Amenaza Regulatoria (EUDR)

A partir de 2026, la UE exigirá que productos como el aguacate cuenten con una **Declaración de Debida Diligencia (DDS)** que pruebe que el producto es "libre de deforestación" (producido en tierras no deforestadas después del 31 de diciembre de 2020) y legal según las leyes del país de origen.

### El "Gap" de Datos

* **Asimetría:** El 83% de los exportadores dependen de datos secundarios. La UE exige geolocalización precisa (polígonos) y datos primarios.
* **Riesgo Operativo:** La validación manual de miles de hectáreas es inviable.
* **Consecuencias:** Multas del 4% de la facturación anual en la UE, confiscación de carga y desplazamiento por competidores como Perú.

---

## 4. Análisis de Mercado y Prospectos ("Goliats")

Nuestro modelo de negocio B2B se enfoca en los grandes exportadores que no pueden permitirse interrupciones en su cadena de suministro.

| Prospecto Clave | Valor Est. Exportación | Riesgo de Multa (4%) | Hub de Entrada UE |
| --- | --- | --- | --- |
| **Avocados From Mexico** | ~$700 M USD | $28.0 M USD | Países Bajos / España |
| **FruitCom** | ~$600 M USD | $24.0 M USD | Países Bajos |
| **Del Monte Fresh** | ~$400 M USD | $16.0 M USD | Francia / Alemania |
| **Mission Produce** | ~$350 M USD | $14.0 M USD | Reino Unido |

*Nota: Cifras estimadas basadas en volúmenes de exportación y precios promedio de mercado.*

---

## 5. Propuesta Técnica y Uso de Recursos (Hackathon Specs)

Para cumplir con el requisito de que "el valor del proyecto está en cómo se usan los datos", nuestra arquitectura integra fuentes sugeridas en el Anexo Técnico con datos locales.

### Arquitectura del MVP (Entregable de 48 horas)

#### Capa 1: Verificación de Deforestación (Caso A)

* **Fuente de Datos:** Global Forest Watch (API) y Sentinel-2.
* **Lógica:** Análisis de alertas GLAD/RADD dentro del polígono del productor.
* 
**Cálculo de Impacto:** Si se detecta pérdida de cobertura arbórea, utilizamos la **API de Climatiq**  para estimar el carbono liberado () por el cambio de uso de suelo. Esto añade valor al reporte de sostenibilidad corporativo (Scope 3).



#### Capa 2: Verificación Hídrica (Caso B)

* 
**Fuente Global:** **Aqueduct - Water Risk Atlas (WRI)**. Usamos esta API para determinar el nivel de estrés hídrico basal de la región.


* 
**Fuente Climática:** **Open-Meteo API**. Consultamos "Historical weather"  para validar patrones de precipitación en el predio y contrastarlos con supuestos de riego.


* **Fuente Local:** Cruce con mapas estáticos de acuíferos de CONAGUA (Simulado mediante base de datos local para el demo).

#### Capa 3: Motor de Decisión y Salida

* **Procesamiento:** Python backend que cruza las capas 1 y 2.
* **Salida (Output):** Generación de un archivo JSON estructurado que simula el formato requerido por el sistema **TRACES NT** de la Unión Europea.
* 
*Justificación:* El anexo permite "simular operaciones" y generar "logs realistas", reconociendo la dificultad de integrarse a sistemas gubernamentales reales en un fin de semana.





---

## 6. Definición del MVP (Minimum Viable Product)

El entregable final para el hackathon será un prototipo funcional que demuestre el "Happy Path" y el "Blocking Path" de una exportación.

**Funcionalidades Clave:**

1. **Ingesta de Polígono:** Interfaz web (mapa interactivo) donde el usuario carga el archivo `.geojson` de su huerta o dibuja el perímetro.
2. **Semáforo de Cumplimiento (Dashboard):**
* 🟢 **Verde:** Sin deforestación > 2020 + Riesgo Hídrico Aceptable.
* 🔴 **Rojo:** Deforestación detectada O Zona de Veda Hídrica.


3. **Generador de Evidencia:**
* Para casos aprobados: Descarga de un "Certificado de Conformidad GreenPass" (PDF) y el archivo de datos (JSON) para aduanas.
* Para casos rechazados: Reporte detallado de la infracción (e.g., "Pérdida de cobertura arbórea detectada en Feb 2022 - 120 toneladas CO2e estimadas").



---

## 7. Análisis Financiero y Modelo de Negocio

### Modelo de Ingresos: Transactional SaaS

* **Cobro por Hectárea/Año:** Suscripción para monitoreo continuo de la base de proveedores.
* **Cobro por Certificado de Embarque:** Micro-transacción por cada lote exportado que requiere el token de validación.

### Viabilidad Económica

El costo de nuestra solución es marginal comparado con el riesgo.

* **Costo del Problema:** Una multa del 4% sobre $100M USD de exportación son **$4 Millones de USD**.
* **Costo de la Solución:** Monitorear esas mismas hectáreas podría costar ~$50k - $100k USD anuales.
* **ROI Inmediato:** El retorno de inversión es superior al 40x solo por prevención de multas, sin contar el valor de mantener el acceso al mercado.

---

## 8. Marco Normativo y Cumplimiento

El proyecto se rige estrictamente por:

1. **Reglamento (UE) 2023/1115 (EUDR):** Artículo 9 (Requisitos de información) y Artículo 10 (Evaluación de riesgo). GreenPass automatiza estos artículos.
2. **Norma Mexicana NMX-AA-179-SCFI-2018 / NIS B-1:** Relativa a la medición de agua. Al integrar datos de estrés hídrico, ayudamos a las empresas a alinearse con los reportes nacionales de sustentabilidad.
3. 
**GHG Protocol:** Utilizamos factores de emisión estándar para traducir la deforestación en impacto de carbono, dando "estructura conceptual a la solución" como sugiere el anexo.



---

## 9. Conclusión para los Jueces

GreenPass no es solo una herramienta de visualización; es infraestructura crítica para el comercio exterior de México. Mientras otros proyectos crean conciencia, nosotros creamos **continuidad operativa**.

Utilizamos datos avanzados (WRI, GFW, Climatiq) no para hacer gráficos bonitos, sino para tomar decisiones binarias de negocio: **Exportar o No Exportar**. Esta es la definición de "transformar señales climáticas complejas en acciones claras".