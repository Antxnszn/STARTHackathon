# **🎫 Ciclo de Vida del Certificado EUDR (Workflow)**

Este documento detalla el proceso técnico y operativo mediante el cual GreenPass obtiene el "Due Diligence Statement" (DDS) válido para la exportación.

## **1\. El Proceso en la Vida Real (Producción)**

En un entorno real, GreenPass actuaría como un software "Middleware" autorizado por la Comisión Europea.

### **Paso 1: La Auditoría Interna (GreenPass)**

El exportador sube su polígono a GreenPass. Nuestro sistema valida:

* ✅ No hay deforestación (Global Forest Watch).  
* ✅ Riesgo de agua aceptable (WRI/CONAGUA).  
* ✅ Datos del productor correctos.

### **Paso 2: La Transmisión (API Push)**

Si la auditoría es verde, GreenPass empaqueta los datos en el JSON (que definimos en GreenPass\_EUDR\_Payload\_Spec.md) y lo envía a la API de la UE.

* **Endpoint Real:** POST https://webgate.ec.europa.eu/tracesnt/api/v2/dds  
* **Autenticación:** Certificado Digital X.509 (Gobierno a Gobierno).

### **Paso 3: Validación Europea**

El sistema TRACES NT recibe el JSON y hace sus propias verificaciones automáticas:

* ¿El polígono está en el mar?  
* ¿El EORI (ID de empresa) existe?  
* ¿El polígono se traslapa con otro?

### **Paso 4: Emisión del "Certificado" (El Token)**

Si todo es correcto, TRACES NT responde con un **Código de Referencia Único**.

**Ejemplo de Respuesta Real:**

24MX08044000123456

Este código **ES** el certificado.

### **Paso 5: Aduana**

El exportador imprime este código en su Factura Comercial y Bill of Lading. El oficial de aduanas en Rotterdam escanea el código y ve en su pantalla: "Aprobado".

## **2\. El Proceso en el Hackathon (Simulación)**

Dado que no tenemos credenciales del gobierno europeo, simularemos la "Caja Negra" de TRACES NT.

### **Tu Estrategia de Demo:**

1. **El Usuario hace clic en:** "Generar Pasaporte Digital".  
2. **Tu Backend (Server 1):** Valida internamente que no haya deforestación.  
3. **Tu Backend:** Simula una llamada a la UE (puede ser una función interna mock\_submit\_to\_eu()).  
4. **Respuesta Simulada:** Tu sistema genera un código aleatorio con el formato real:  
   * GP (GreenPass)  
   * 26 (Año 2026\)  
   * MX (México)  
   * AG (Aguacate)  
   * 88291 (Secuencial)  
   * **Resultado:** GP-26-MX-AG-88291

### **3\. Visualización del Entregable (Frontend)**

Para el juez, el "Certificado" se debe ver como un documento oficial. Puedes generar un PDF simple que contenga:

1. **Código QR:** Que contenga el JSON de los datos.  
2. **Referencia:** El código GP-26-MX-AG-88291 en grande y negrita.  
3. **Estado:** "EUDR COMPLIANT".  
4. **Mapa:** Una imagen pequeña del polígono de la huerta.

*"Este documento PDF es el comprobante físico, pero el valor real es el código digital que nuestro sistema inyectó en la base de datos de la UE."*