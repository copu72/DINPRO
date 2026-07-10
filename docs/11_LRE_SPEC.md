# LRE — Linear Referencing Engine

**Especificación Funcional v0.1**
**Versión objetivo:** v0.4.0
**Estado:** RFC Aprobada → SPEC

---

## 01. Objetivo

El Linear Referencing Engine (LRE) es el módulo de DINPRO que extiende el sistema de PK básico del GSE para convertirlo en un motor completo de referenciación lineal. Proporciona estacionamiento avanzado, eventos lineales, segmentación dinámica, proyecciones laterales, calibración de rutas y perfil longitudinal.

El LRE es la capa sobre la que se apoyarán todos los módulos funcionales (Municipios, Carreteras, Hidrografía, Infraestructuras, Catastro) para responder preguntas como:

- ¿En qué PK comienza y termina esta entidad?
- ¿Qué longitud de eje está afectada?
- ¿Qué geometría corresponde a este tramo?
- ¿Qué eventos coinciden en este rango de PK?

---

## 02. Alcance

### Incluye

- Stationing avanzado con precisión configurable y múltiples formatos de salida
- Proyecciones laterales (offset point, left/right desde un PK con distancia)
- Segmentación dinámica (tramos continuos, discontinuos, superpuestos)
- Rutas y calibración (ajuste de PK cuando hay discrepancia geometría vs. PK teórico)
- Perfil longitudinal (pendiente acumulada, rasante, puntos singulares)
- Eventos lineales versionados (asociar atributos a un rango de PK con trazabilidad)
- Concurrencia de eventos (intersecciones de rangos, solapamientos)
- Sistema de medidas (Measure System) desacoplado de la geometría del eje
- Exportación a CSV, GeoJSON, Excel

### Excluye

- Operaciones geométricas complejas (buffer, clip) → ya están en GSE SpatialOperations
- Validación topológica → ya está en GSE TopologyValidator
- Transformación CRS → ya está en GSE Transformer
- Interfaz de usuario (el LRE es un motor, no una UI)
- Almacenamiento persistente de eventos (se delega en el módulo/cliente que use el LRE)

---

## 03. Arquitectura

El LRE se apoya en el GSE y extiende sus capacidades sin modificar el núcleo existente. La separación clave es:

```
GSE (v0.3.0)
├── Geometry (Point, Line, Polyline, etc.)
├── CRS / Transform
├── SpatialOperations
├── TopologyValidator
└── LinearReferencing (básico: point_at_pk, pk_at_point, azimuth, etc.)

LRE (v0.4.0)
├── MeasureSystem          ← NUEVO: desacopla medida de geometría
├── AdvancedStationing     ← NUEVO: formatos, precisión, calibración
├── LateralProjection      ← NUEVO: offset point left/right
├── DynamicSegmentation    ← NUEVO: tramos, concurrencia, solapamientos
├── LongitudinalProfile    ← NUEVO: pendiente acumulada, rasante
├── LinearEvent            ← NUEVO: evento versionado con rango PK
├── RouteCalibration       ← NUEVO: ajuste PK teórico vs. geométrico
└── LRE Exports            ← NUEVO: CSV, GeoJSON, Excel
```

### Dependencias

```
LRE ────► GSE (Geometry, CRS, LinearReferencing existente)
   │
   └────► stdlib (csv, json, math, dataclasses)
```

El LRE no añade dependencias externas. Para exportación a Excel se usará openpyxl solo si está disponible (adapter pattern, igual que pyproj en CRS).

---

## 04. Measure System

### Problema

Actualmente, `LinearReferencing` liga la medida (PK) directamente a la distancia geométrica acumulada sobre la Polyline:

```
PK.value = distancia_geometrica_acumulada
```

Esto impide:
- Ejes con PK discontinuos (ej: PK 0+000 a 2+000, salto a PK 5+000)
- Ejes con reinicios de kilometración (ej: dos tramos con PK 0+000 cada uno)
- Calibración donde el PK teórico difiere de la distancia real
- Múltiples sistemas de medida sobre la misma geometría

### Solución: MeasureSystem

Se introduce `MeasureSystem` como objeto que encapsula la relación entre la geometría y la medida lineal:

```python
class MeasureSystem:
    """
    Relaciona una medida lineal (m) con una distancia geométrica (m)
    sobre una Polyline.

    Por defecto: medida = distancia (sistema directo).
    Puede calibrarse para soportar desfases, discontinuidades y reinicios.
    """
```

Un MeasureSystem contiene:
- **CalibrationPoints:** lista de puntos de calibración que asocian (PK, distancia_geometrica). Si no hay calibración, medida == distancia.
- **Discontinuities:** lista de saltos donde la medida se reinicia o salta.
- **Direction:** forward (PK creciente con la geometría) o reverse (PK decreciente).

Así, la misma geometría puede tener múltiples MeasureSystem (ej: uno por cada carretera que comparte un tramo).

### Impacto en Axis

```python
class Axis:
    # Existente
    def point_at_pk(self, pk) -> Point          # usa MeasureSystem por defecto

    # Nuevo
    def with_measure_system(self, ms) -> Axis    # crea un Axis con MeasureSystem propio
    @property
    def measure_systems(self) -> list[MeasureSystem]
```

---

## 05. API pública

### MeasureSystem

```python
@dataclass
class CalibrationPoint:
    pk: float           # PK teórico (ej: 25350.0)
    distance: float     # distancia geométrica (ej: 25280.0)

@dataclass
class MeasureDiscontinuity:
    start_pk: float
    end_pk: float
    gap_before: float   # distancia geométrica del salto

class MeasureSystem:
    def __init__(self, axis: Axis, calibrations: list[CalibrationPoint] | None = None)
    def pk_at_distance(self, distance: float) -> float
    def distance_at_pk(self, pk: float) -> float
    def calibrate(self, points: list[CalibrationPoint]) -> None
    def add_discontinuity(self, pk: float, gap: float) -> None
    def total_measure(self) -> float               # PK final considerado
```

### AdvancedStationing

```python
class AdvancedStationing:
    def __init__(self, axis: Axis, measure_system: MeasureSystem | None = None)

    def point_at_pk(self, pk: PK | str | float) -> Point
    def pk_at_point(self, point: Point) -> PK
    def nearest_pk(self, point: Point) -> tuple[Point, PK, float]

    # Formateo
    def format_pk(self, pk: PK, format: str = "default") -> str
        # formatos: "default" (PK 25+350), "decimal" (25350.000),
        #           "km" (25.350), "segmented" (25+350.000)

    def set_precision(self, decimals: int) -> None
    def set_output_format(self, fmt: str) -> None
```

### LateralProjection

```python
class LateralProjection:
    def __init__(self, axis: Axis)

    def offset_point(self, pk: PK | str | float, distance: float,
                     side: str = "left") -> Point
        # Devuelve el punto desplazado perpendicularmente

    def offset_points(self, pk_start: PK, pk_end: PK, distance: float,
                      side: str = "left", step: float = 20.0) -> list[tuple[PK, Point]]
        # Devuelve una lista de puntos offset en un rango de PK

    def cross_section(self, pk: PK | str | float, width: float) -> tuple[Point, Point]
        # Devuelve (left_point, right_point) para una sección transversal

    def left(self, pk: PK | str | float, distance: float) -> Point
    def right(self, pk: PK | str | float, distance: float) -> Point
        # Azúcar sintáctico para offset_point con side fijo
```

### DynamicSegmentation

```python
@dataclass
class LinearSegment:
    pk_start: PK
    pk_end: PK
    length: float
    attributes: dict

class DynamicSegmentation:
    def __init__(self, axis: Axis)

    def split_by_events(self, events: list[LinearEvent]) -> list[LinearSegment]
        # Divide el eje según los rangos de los eventos

    def merge_segments(self, segments: list[LinearSegment]) -> list[LinearSegment]
        # Fusiona segmentos contiguos con mismos atributos

    def clip(self, pk_start: PK, pk_end: PK) -> Polyline
        # Devuelve la subgeometría correspondiente al rango PK

    def intersection(self, a: LinearSegment, b: LinearSegment) -> LinearSegment | None
        # Intersección de dos segmentos (misma ruta)

    def contains(self, outer: LinearSegment, inner: LinearSegment) -> bool
        # Comprueba si un segmento contiene completamente a otro
```

### LinearEvent (versionado)

```python
@dataclass
class LinearEvent:
    event_id: str
    event_type: str
    pk_start: PK
    pk_end: PK
    attributes: dict
    version: int = 1          # ← versionado para auditoría
    revision: str = ""        # ← hash o timestamp de la revisión
    created_at: str = ""      # ISO 8601
    updated_at: str = ""      # ISO 8601

class LinearEventSet:
    def __init__(self, events: list[LinearEvent] | None = None)

    def add(self, event: LinearEvent) -> None
    def remove(self, event_id: str) -> None
    def update(self, event_id: str, attributes: dict) -> LinearEvent
        # Al actualizar, incrementa version y actualiza updated_at

    def query(self, pk: PK) -> list[LinearEvent]
        # Devuelve eventos que contienen un PK dado

    def query_range(self, pk_start: PK, pk_end: PK) -> list[LinearEvent]
        # Devuelve eventos cuyo rango intersecta con [pk_start, pk_end]

    def overlaps(self) -> list[tuple[LinearEvent, LinearEvent]]
        # Devuelve pares de eventos solapados

    def gaps(self) -> list[LinearSegment]
        # Devuelve los segmentos sin cobertura de eventos

    def to_dataframe(self) -> Any
        # Exporta a pandas.DataFrame si está disponible

    def audit_trail(self, event_id: str) -> list[LinearEvent]
        # Historial de versiones de un evento
```

### RouteCalibration

```python
class RouteCalibration:
    def __init__(self, axis: Axis)

    def auto_calibrate(self, known_points: list[tuple[PK, Point]]) -> MeasureSystem
        # Calcula automáticamente el MeasureSystem a partir de puntos conocidos
        # Detecta desfases lineales y genera puntos de calibración

    def adjust_pk(self, pk: PK, offset: float) -> PK
        # Aplica un ajuste manual a un PK

    def reset_pk(self, new_start_pk: PK) -> MeasureSystem
        # Reinicia la kilometración desde un nuevo PK inicial

    def validate_calibration(self, measure_system: MeasureSystem) -> list[str]
        # Valida la consistencia de una calibración: errores > 1% → warning
```

### LongitudinalProfile

```python
@dataclass
class ProfilePoint:
    pk: PK
    elevation: float
    slope: float          # pendiente en tanto por ciento
    accumulated_length: float

class LongitudinalProfile:
    def __init__(self, axis: Axis)

    def profile(self, step: float = 20.0) -> list[ProfilePoint]
        # Perfil longitudinal completo a intervalos regulares

    def slope_segments(self, tolerance: float = 0.5) -> list[LinearSegment]
        # Segmentos de pendiente constante (rasante)

    def maximum_slope(self) -> tuple[PK, float]
        # PK y valor de la pendiente máxima

    def critical_points(self) -> list[ProfilePoint]
        # Puntos singulares: cambios de rasante, pendiente máxima, etc.

    def accumulated_climb(self) -> float
        # Desnivel positivo acumulado
```

### LRE Exports

```python
class LREExporter:
    def __init__(self, axis: Axis)

    def to_csv(self, events: list[LinearEvent], path: str) -> None
    def to_geojson(self, events: list[LinearEvent], path: str) -> None
    def to_excel(self, events: list[LinearEvent], path: str) -> None
        # Excel solo si openpyxl está disponible
```

---

## 06. Modelo de datos

### Eventos lineales versionados

```
LinearEvent
├── event_id: str              # UUID o identificador único
├── event_type: str            # Tipo semántico: "municipio", "carretera", "rio"
├── pk_start: PK               # PK de inicio
├── pk_end: PK                 # PK de fin
├── geometry: Polyline | None  # Geometría asociada (opcional)
├── attributes: dict           # Atributos arbitrarios del evento
├── version: int               # Número de versión (comienza en 1)
├── revision: str              # Hash del contenido o timestamp ISO 8601
├── created_at: str            # Fecha de creación (ISO 8601)
├── updated_at: str            # Fecha de última modificación (ISO 8601)
└── metadata: dict             # Metadatos adicionales (origen, autor, etc.)
```

### Sistema de calibración

```
MeasureSystem
├── axis_id: str
├── calibrations: list[CalibrationPoint]
│   └── CalibrationPoint(pk, distance)   # pk = PK teórico, distance = distancia geométrica
├── discontinuities: list[MeasureDiscontinuity]
│   └── MeasureDiscontinuity(start_pk, end_pk, gap_before)
└── direction: str                       # "forward" | "reverse"
```

### Formato de exportación GeoJSON

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[...], [...]]
      },
      "properties": {
        "event_id": "MUN-001",
        "event_type": "municipio",
        "pk_start": "PK 25+350",
        "pk_end": "PK 27+120",
        "version": 1,
        "attributes": {
          "nombre": "Alcalá de Henares",
          "provincia": "Madrid"
        }
      }
    }
  ]
}
```

---

## 07. Casos de uso

### UC-01: Determinar qué municipios atraviesa una carretera

1. El módulo de Municipios carga los términos municipales como `LinearEvent[]`
2. LRE `LinearEventSet.query_range(PK(0), PK(50000))` devuelve todos los municipios que intersectan con el eje
3. `DynamicSegmentation.split_by_events(events)` divide el eje en tramos por municipio
4. Resultado: lista de (tramo, municipio, PK_inicio, PK_fin, longitud)

### UC-02: Obtener el perfil longitudinal de un eje

1. El usuario selecciona un eje de 50 km
2. `LongitudinalProfile.profile(step=100)` genera 500 puntos de perfil
3. `LongitudinalProfile.maximum_slope()` identifica el punto con mayor pendiente
4. `LongitudinalProfile.slope_segments()` agrupa por tramos de pendiente constante

### UC-03: Cruce de un río con una carretera

1. El módulo de Hidrografía proporciona la geometría del río
2. `SpatialOperations.intersection(eje, rio)` (del GSE) obtiene el punto de cruce
3. `AdvancedStationing.pk_at_point(punto_cruce)` da el PK exacto
4. Se crea un `LinearEvent` con el cruce en el PK correspondiente

### UC-04: Calcular proyección lateral de un eje

1. `LateralProjection.offset_points(PK(1000), PK(2000), distance=50, side="left", step=20)`
2. Devuelve 50 puntos offset a la izquierda del eje para generar un corredor

### UC-05: Calibrar un eje con PK teórico discrepante

1. El eje importado tiene PK teóricos que no coinciden con la distancia geométrica
2. El usuario proporciona 3 puntos de calibración conocidos (PK, coordenada)
3. `RouteCalibration.auto_calibrate(puntos)` genera un `MeasureSystem` con los desfases
4. Todas las consultas posteriores usan el sistema calibrado

### UC-06: Detectar solapamientos en la misma ruta

1. Dos eventos (carretera A y carretera B) comparten un tramo del eje
2. `LinearEventSet.overlaps()` devuelve los pares solapados
3. `DynamicSegmentation.split_by_events()` genera tramos no solapados

### UC-07: Exportar eventos a GeoJSON para GIS

1. El usuario selecciona los eventos de municipios en el rango PK 0-10000
2. `LREExporter.to_geojson(events, "municipios.geojson")`
3. El archivo se abre en QGIS para validación visual

### UC-08: Auditoría de cambios en eventos

1. Un evento de carretera se actualiza (cambia su PK_fin)
2. `LinearEventSet.update(...)` incrementa `version` y registra `updated_at`
3. `LinearEventSet.audit_trail(event_id)` muestra el historial completo de cambios

---

## 08. Integración con el GSE existente

El LRE extiende, no reemplaza, las clases existentes:

| Clase existente (GSE) | Clase nueva (LRE) | Relación |
|---|---|---|
| `LinearReferencing` | `AdvancedStationing` | Extiende con formatos y precisión |
| `PK` | — | Se mantiene igual, LRE lo utiliza |
| `Station` | — | Se mantiene igual |
| `Axis` | — | Se añaden métodos: `with_measure_system`, `measure_systems` |
| — | `MeasureSystem` | Nuevo, desacopla medida de geometría |
| — | `LateralProjection` | Usa `Axis`, `Vector` y `Line` del GSE |
| — | `DynamicSegmentation` | Usa `Polyline`, `SpatialOperations` del GSE |
| — | `LinearEvent` / `LinearEventSet` | Nuevo, modelo de eventos versionados |
| — | `RouteCalibration` | Usa `MeasureSystem` y `PK` |
| — | `LongitudinalProfile` | Usa `Axis`, `PK`, `Point` |
| — | `LREExporter` | Nuevo, serialización |

---

## 09. Rendimiento

### Objetivos

| Operación | Objetivo |
|-----------|----------|
| point_at_pk con calibración | < 2 ms |
| pk_at_point con calibración | < 10 ms |
| offset_point (único) | < 1 ms |
| offset_points (100 pts) | < 50 ms |
| DynamicSegmentation.split (100 eventos) | < 100 ms |
| LinearEventSet.query_range (1000 eventos) | < 50 ms |
| LongitudinalProfile.profile (1000 pts) | < 500 ms |
| RouteCalibration.auto_calibrate (10 pts) | < 100 ms |

### Estrategias

- Los `CalibrationPoint` se almacenan ordenados para búsqueda O(log n) con bisect.
- La interpolación entre puntos de calibración es lineal (suficiente para la precisión requerida).
- `LinearEventSet` usa un índice interno basado en PK_start para consultas rápidas por rango.
- Las operaciones de perfil longitudinal se paralelizan por tramos independientes.

---

## 10. Tolerancias

| Parámetro | Valor por defecto | Configurable |
|-----------|-------------------|--------------|
| Precisión de PK (output) | 0.001 m (1 mm) | Sí |
| Precisión interna de calibración | 0.001 m | Sí |
| Tolerancia de calibración (error) | 1.0 % | Sí |
| Tolerancia de solapamiento | 0.01 m | Sí |
| Paso de perfil longitudinal | 20.0 m | Sí |

---

## 11. Excepciones

| Excepción | Cuándo se lanza |
|-----------|-----------------|
| `LREError` (base) | — |
| `CalibrationError` | Puntos de calibración inconsistentes |
| `EventNotFoundError` | `event_id` no existe en el conjunto |
| `OverlappingEventError` | Intento de añadir evento con solapamiento no permitido |
| `InvalidRangeError` | pk_start > pk_end |
| `ExportError` | Fallo en exportación |

---

## 12. Criterios de aceptación

El LRE se considera aceptado cuando se cumplan TODAS las condiciones siguientes:

- [ ] MeasureSystem implementado con calibración, discontinuidades y dirección
- [ ] MeasureSystem permite PK discontinuos y reinicios de kilometración
- [ ] AdvancedStationing con formatos "default", "decimal", "km", "segmented"
- [ ] LateralProjection: offset_point, offset_points, cross_section, left, right
- [ ] DynamicSegmentation: split_by_events, merge_segments, clip, intersection, contains
- [ ] LinearEvent versionado: version, revision, created_at, updated_at, audit_trail
- [ ] LinearEventSet: add, remove, update, query, query_range, overlaps, gaps
- [ ] RouteCalibration: auto_calibrate, adjust_pk, reset_pk, validate_calibration
- [ ] LongitudinalProfile: profile, slope_segments, maximum_slope, accumulated_climb
- [ ] LREExporter: to_csv, to_geojson, to_excel (si openpyxl disponible)
- [ ] Sin dependencias externas obligatorias (openpyxl opcional)
- [ ] Cobertura de tests ≥ 90 %
- [ ] Ruff: 0 errores
- [ ] Compatibilidad hacia atrás: el código existente que usa LinearReferencing no se rompe
- [ ] Documentación: esta SPEC + ejemplos de uso para cada clase pública

---

## 13. ADR asociados

| ADR | Título | Relación |
|-----|--------|----------|
| ADR-0002 | Inversión de dependencias | El LRE no depende de capas superiores |
| ADR-0004 | Geometry Engine (GSE) | El LRE se apoya en el GSE |
| ADR-0006 | Arquitectura tres capas | El LRE pertenece a la capa de dominio |
| ADR-0007 | Calidad por Sprint | Esta SPEC sigue el flujo establecido |

---

## 14. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Calibración imprecisa con pocos puntos | Media | Medio | Documentar límites; validar con error > 1% |
| Rendimiento con ejes de > 10000 eventos lineales | Baja | Medio | Índice interno en LinearEventSet |
| Solapamientos no detectados | Baja | Alto | Tests exhaustivos de DynamicSegmentation |
| Dependencia de openpyxl para Excel | Media | Bajo | Hacer opcional con adapter pattern |
| Complejidad del MeasureSystem | Alta | Medio | Empezar con sistema directo (medida == distancia) y añadir calibración en iteración posterior |

---

*Documento generado como parte del proceso de calidad de DINPRO.*
*RFC Aprobada por Architect Review — Pendiente de implementación en Sprint 4*
