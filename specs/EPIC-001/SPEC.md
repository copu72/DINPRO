# EPIC-001: Linear Referencing Engine

## SPEC — Especificación Funcional

**Versión objetivo:** v0.4.0
**Estado:** Aprobada

---

### 01. Objetivo

Motor completo de referenciación lineal que extiende el GSE. Proporciona estacionamiento avanzado, eventos lineales versionados, segmentación dinámica, proyecciones laterales, calibración de rutas y perfil longitudinal.

### 02. Alcance

**Incluye:**
- MeasureSystem: desacopla medida lineal de geometría del eje
- AdvancedStationing: formatos de PK, precisión configurable
- LateralProjection: offset point, sección transversal
- DynamicSegmentation: división por eventos, fusión, recorte
- LinearEvent versionado: trazabilidad y auditoría
- RouteCalibration: ajuste PK teórico vs. geométrico
- LongitudinalProfile: pendiente acumulada, rasante
- LREExporter: CSV, GeoJSON, Excel (opcional)

**Excluye:**
- Operaciones geométricas complejas (GSE)
- Validación topológica (GSE)
- Transformación CRS (GSE)
- Interfaz de usuario
- Almacenamiento persistente de eventos

### 03. Arquitectura

```
GSE (v0.3.0)
├── Geometry / CRS / SpatialOperations / LinearReferencing

LRE (v0.4.0)
├── MeasureSystem          ← desacopla medida de geometría
├── AdvancedStationing     ← formatos, precisión, calibración
├── LateralProjection      ← offset point left/right
├── DynamicSegmentation    ← tramos, concurrencia, solapamientos
├── LinearEvent            ← evento versionado con rango PK
├── RouteCalibration       ← ajuste PK teórico vs. geométrico
├── LongitudinalProfile    ← pendiente acumulada, rasante
└── LREExporter            ← CSV, GeoJSON, Excel
```

### 04. Dependencias

```
LRE ────► GSE (Geometry, CRS, Axis, LinearReferencing)
   │
   └────► stdlib (csv, json, math, dataclasses, bisect)
```

Cero dependencias externas obligatorias. openpyxl opcional para Excel.

### 05. Tolerancias

| Parámetro | Defecto | Configurable |
|-----------|---------|--------------|
| Precisión PK output | 0.001 m | Sí |
| Precisión calibración | 0.001 m | Sí |
| Tolerancia calibración | 1.0 % | Sí |
| Tolerancia solapamiento | 0.01 m | Sí |
| Paso perfil longitudinal | 20.0 m | Sí |

### 06. Excepciones

| Excepción | Uso |
|-----------|-----|
| `CalibrationError` | Puntos de calibración inconsistentes |
| `EventNotFoundError` | event_id no existe |
| `InvalidRangeError` | pk_start > pk_end |
| `ExportError` | Fallo en exportación |

### 07. Criterios de aceptación globales

- [ ] Los 9 micro-sprints completados con sus tests individuales
- [ ] Cobertura de tests ≥ 90 % para todo el LRE
- [ ] Ruff: 0 errores
- [ ] Compatibilidad hacia atrás: GSE existente no se rompe
- [ ] Documentación completa en specs/EPIC-001/
- [ ] Benchmarks dentro de objetivos
