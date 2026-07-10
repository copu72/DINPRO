# Domain Glossary

> Diccionario oficial de términos del dominio DINPRO.
> Cada término tiene una definición única y autorizada.
> Versión: 0.3.1-dev

---

## A

### AnalysisPipeline

Secuencia de operaciones de análisis aplicadas sobre un proyecto. Encadena
transformaciones geométricas, espaciales y lineales sin intervención manual.

### Axis

Entidad lineal de primer orden que representa un eje geométrico (carretera,
ferrocarril, canal, tubería). Contiene una polilínea, un CRS opcional y un
sistema de referencia lineal (LRE). Es el concepto central sobre el que se
construyen el resto de módulos del dominio.

---

## C

### Calibration (Calibración)

Relación entre un punto de la geometría del eje y su valor de PK medido en
campo. Permite ajustar la medida lineal para reflejar discrepancias entre la
geometría teórica y la realidad. Se representa mediante `CalibrationPoint`.

### CRS (Coordinate Reference System)

Sistema de referencia de coordenadas. Define cómo se interpretan las coordenadas
de la geometría en relación con la superficie terrestre. DINPRO soporta CRS
predefinidos (ETRS89, UTM, WGS84) y personalizados.

---

## D

### Discontinuity (Discontinuidad)

Salto en la secuencia de PK donde el valor de PK cambia bruscamente sin
correspondencia con la geometría. Ocurre típicamente en cambios de kilometración
o reinicios de trazado. Se representa mediante `MeasureDiscontinuity`.

---

## F

### Feature

Entidad geográfica con significado dentro del dominio (un municipio, un tramo
de carretera, un río, una infraestructura). Contiene geometría, atributos y
relaciones con otras entidades.

---

## G

### Geometry (Geometría)

Representación matemática de formas espaciales. DINPRO implementa su propio
modelo geométrico con `Point`, `Vector`, `Line`, `Polyline`, `Polygon`,
`Circle` y `BoundingBox`. No depende de librerías externas de geometría.

---

## L

### LinearEvent (Evento Lineal)

Evento localizado sobre un eje mediante medida lineal (PK). Puede ser puntual
(PK exacto) o segmentado (PK inicial - PK final). Ejemplos: incidente, cambio
de firme, señalización, velocidad máxima.

### LinearReferencing (LRE)

Motor de referencia lineal sobre una polilínea. Proporciona operaciones para
localizar puntos sobre la geometría a partir de una medida de distancia:
`point_at_pk`, `pk_at_point`, azimuth, tangente, normal, pendiente, curvatura.

---

## M

### Measure (Medida Lineal)

Valor numérico que expresa una posición sobre un eje en unidades de longitud
lineal. Puede estar calibrado (PK) o ser una distancia geométrica cruda.

### MeasureSystem

Servicio del dominio que gestiona la relación entre la geometría del eje y la
medida lineal. Soporta calibraciones, discontinuidades y múltiples sistemas
de medida asociados a un mismo eje.

---

## P

### PK (Punto Kilométrico)

Medida lineal expresada en el formato clásico de infraestructuras lineales.
Compuesto de kilómetros + metros (ej: `15+345.20`). Es la unidad de medida
fundamental del LRE.

### Project (Proyecto)

Contenedor principal del estado de DINPRO. Agrupa axis, settings, logger,
resultados, plugins y eventos. Es la unidad de persistencia del sistema.

---

## S

### Station

Value Object inmutable que representa una medida lineal del dominio. Internamente
es un `float`, pero se comporta como un concepto propio con propiedades
(`kilometer`, `meter`), comparación (`<`, `>`, `==`), hash, y formateo
configurable mediante estrategias (`Classic`, `Decimal`, `Engineering`, `Custom`).

---

## T

### Topology (Topología)

Conjunto de reglas de validación geométrica: detección de auto-intersecciones,
longitud cero, vértices duplicados, orientación de polígonos. Implementado
mediante `TopologyValidator`.

---

## V

### Value Object

Objeto inmutable del dominio cuya identidad se basa en sus atributos, no en un
identificador. Ejemplos en DINPRO: `Station`, `PK`, `Point`, `Vector`, `CRS`.
Son comparables, hasheables y sin efectos secundarios.

---

## Historial

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-07-10 | 0.3.1-dev | Creación inicial con términos del GSE y LRE |
