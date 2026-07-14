# EPIC-002 — Spatial Query Engine (SPEC Funcional)

**Versión:** 0.1
**Estado:** Preliminar

---

## 1. Propósito

Proporcionar un motor de consultas espaciales que relacione geometrías externas con el sistema de referenciación lineal de DINPRO, permitiendo a los módulos funcionales (Municipios, Carreteras, etc.) responder preguntas del tipo "¿qué intersecta este eje?" sin implementar lógica espacial propia.

## 2. Funcionalidades

### F-01: Indexado de geometrías externas

El motor debe aceptar colecciones de geometrías (Polygon, Polyline, Point) acompañadas de metadatos arbitrarios, y almacenarlas para consultas posteriores.

### F-02: Consulta de intersección con el eje

Debe devolver todas las geometrías indexadas que intersectan el eje del proyecto, indicando para cada una:
- PK de entrada
- PK de salida
- Punto de entrada (coordenadas)
- Punto de salida (coordenadas)
- Longitud afectada

### F-03: Consulta de intersección con corredor

Como F-02, pero considerando un corredor de ancho configurable a cada lado del eje.

### F-04: Consulta por rango de PK

Debe limitar los resultados a un rango específico de PK, permitiendo consultas parciales del eje.

### F-05: Generación de eventos lineales

Debe poder convertir los resultados de intersección en eventos lineales del LRE, heredando los metadatos de la geometría original.

## 3. Criterios de aceptación

| ID | Criterio | Verificación |
|---|---|---|
| CA-01 | Indexar 10 geometrías y consultar devuelve las 10 | Test unitario |
| CA-02 | Geometría que intersecta el eje se detecta correctamente | Test con geometría conocida |
| CA-03 | Geometría que NO intersecta el eje no aparece en resultados | Test con geometría alejada |
| CA-04 | Corredor de 50 m detecta geometrías hasta 50 m del eje | Test paramétrico |
| CA-05 | Resultados ordenados por PK ascendente | Assert en test |
| CA-06 | affected_length = exit_pk - entry_pk | Assert en test |
| CA-07 | SQE sin dependencias de tipos de entidades | Revisión de imports |
| CA-08 | to_events produce objetos LinearEvent válidos | Test unitario |
