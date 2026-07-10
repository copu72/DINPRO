# GSE — Geometry & Spatial Engine

**Especificación Técnica v1.0**
**Versión de referencia:** v0.3.0
**Estado:** Implementada (Architect Review superado)

---

## 01. Objetivo

El Geometry & Spatial Engine (GSE) es el motor matemático y espacial de DINPRO. Proporciona un modelo geométrico propio, independiente de bibliotecas externas, con capacidad para representar, manipular y analizar entidades geométricas en el contexto de infraestructura lineal (carreteras, ríos, ferrocarriles, tuberías) y georreferenciación.

El GSE no es un wrapper de Shapely. Es un modelo de dominio completo que expone una API estable y desacoplada del sistema de coordenadas, del formato de origen de los datos y de la capa de presentación.

---

## 02. Alcance

### Incluye

- Geometrías fundamentales (Point, Line, Polyline, Polygon, Circle, BoundingBox)
- Sistema de coordenadas (CRS) con soporte para ETRS89/UTM, WGS84, geográficas y personalizadas
- Transformaciones entre CRS mediante adapter (pyproj como opcional, fallback con algoritmo UTM aproximado)
- Operaciones espaciales (distancia, intersección, contención, buffer, offset, clip, split, merge)
- Referenciación lineal (PK, estacionamiento, tangente, normal, azimut, pendiente, curvatura)
- Topología y validación geométrica (auto-intersecciones, vértices duplicados, segmentos cero)
- Objeto Axis como entidad de primer nivel para infraestructura lineal
- Validación automática de geometrías de entrada (GeometryValidator)
- Sistema de tolerancias configurable

### Excluye

- Renderizado o visualización de geometrías
- Lectura/escritura de formatos CAD o GIS (eso pertenece a la capa de adaptadores)
- Operaciones ráster
- Procesamiento de nubes de puntos
- Datos temporales o series temporales

---

## 03. Casos de uso

### UC-01: Carga y validación de un eje de carretera

1. El usuario importa un archivo DXF con un eje de carretera
2. El adaptador DXF extrae una Polyline
3. El GeometryValidator comprueba: sin auto-intersecciones, sin segmentos cero, CRS válido
4. Se crea un objeto Axis con la Polyline y el CRS asignado
5. El módulo de carreteras puede consultar PK, azimut, normal en cualquier punto

### UC-02: Transformación de coordenadas

1. El usuario tiene datos en ETRS89/UTM30N
2. Necesita exportarlos a WGS84 geográficas
3. Transformer.transform() convierte cada vértice
4. Se obtiene un nuevo Axis en el CRS destino

### UC-03: Cálculo de PK en un punto

1. El usuario hace clic en un punto del mapa
2. Axis.nearest_point() devuelve el punto más próximo sobre el eje
3. Axis.pk_at_point() devuelve el PK correspondiente
4. Axis.azimuth() devuelve la dirección de la tangente

### UC-04: División de un eje

1. El usuario marca un PK donde quiere dividir el eje
2. Axis.split_at_pk() devuelve dos nuevos ejes
3. Cada eje mantiene su propia geometría y PK inicial

### UC-05: Validación de geometría de entrada

1. Un plugin recibe una Polyline desde un archivo externo
2. GeometryValidator.validate() comprueba topología y CRS
3. Si hay errores, se rechaza la geometría con un informe detallado

---

## 04. Arquitectura

### Capas

```
┌──────────────────────────────────────────────┐
│            Capa de Presentación               │  CLI, GUI
├──────────────────────────────────────────────┤
│            Capa de Servicios                  │  Core + Plugins
├──────────────────────────────────────────────┤
│     Capa de Dominio (GSE)                     │  ← GSE
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Geometry  │ │   CRS    │ │  Transform   │  │
│  ├──────────┤ ├──────────┤ ├──────────────┤  │
│  │ Spatial  │ │ Topology │ │Linear Ref    │  │
│  └──────────┘ └──────────┘ └──────────────┘  │
│         ┌────────────────────────┐            │
│         │         Axis           │            │
│         └────────────────────────┘            │
└──────────────────────────────────────────────┘
```

### Estructura de directorios

```
src/dinpro/domain/
├── __init__.py               # Exporta toda la API pública
├── axis.py                   # Clase Axis (entidad de primer nivel)
├── geometry_validator.py     # Validación automática de geometrías
├── geometry/
│   ├── point.py              # Point (x, y, z)
│   ├── vector.py             # Vector (dx, dy, dz)
│   ├── line.py               # Line (start, end)
│   ├── polyline.py           # Polyline (vertices, closed)
│   ├── polygon.py            # Polygon (outer, holes)
│   ├── circle.py             # Circle (center, radius)
│   └── bounding_box.py       # BoundingBox (xmin, ymin, xmax, ymax)
├── crs/
│   ├── types.py              # CRSType enum
│   ├── crs.py                # Clase CRS
│   └── registry.py           # CRSRegistry con definiciones predefinidas
├── transform/
│   └── transformer.py        # Transformer con adapter a pyproj
├── spatial/
│   └── operations.py         # SpatialOperations (todos los métodos estáticos)
├── linear_referencing/
│   ├── pk.py                 # PK y Station
│   └── linear_referencing.py # LinearReferencing (asocia Polyline + PK)
├── topology/
│   └── validator.py          # TopologyValidator, ValidationResult, ValidationIssue
└── adapters/
    └── pyproj_adapter.py     # Adaptador a pyproj para transformaciones CRS
```

---

## 05. Modelo matemático

### Sistema de coordenadas

- **Sistema diestro.** Eje X positivo al este, Y positivo al norte, Z positivo hacia arriba.
- La coordenada Z es opcional (por defecto 0.0) y no se utiliza en operaciones 2D.
- Todas las operaciones espaciales básicas son 2D (planimétricas). La coordenada Z se conserva pero no interviene en intersecciones, buffer, etc.

### Precisión

- Tipo nativo: `float` (doble precisión IEEE 754, ~15 dígitos decimales).
- Tolerancia geométrica por defecto: `1e-10` (unidades de coordenada).
- Tolerancia PK por defecto: `0.001` m (1 mm).
- Tolerancia angular por defecto: `1e-6` radianes (~0.000057°).

### Transformaciones

#### UTM ↔ Geográficas (algoritmo de Krüger)

La transformación entre UTM y coordenadas geográficas se implementa mediante el algoritmo de Krüger (proyección transversa de Mercator). Se utiliza cuando pyproj no está disponible.

Parámetros:
- Elipsoide: WGS84 (a = 6378137 m, f = 1/298.257223563)
- Factor de escala: k0 = 0.9996
- Falso Este: 500000 m
- Falso Norte: 0 m (hemisferio norte), 10000000 m (hemisferio sur)

### Referenciación lineal

El sistema de PK se basa en la distancia acumulada a lo largo de una Polyline.

```
PK(n) = Σ(i=0 to n-1) |Vi+1 - Vi|
```

Donde V son los vértices de la Polyline.

#### Tangente
Vector unitario en la dirección del segmento que contiene al PK.

#### Normal
Vector unitario perpendicular a la tangente en el plano XY (giro antihorario).

#### Azimut
Ángulo de la tangente respecto al norte, en grados [0, 360).

#### Curvatura
Variación angular entre segmentos consecutivos dividida por la longitud media.

---

## 06. Modelo de datos

### Point

```
Point(x: float, y: float, z: float = 0.0)
  └─ Propiedades: x, y, z
  └─ distance_to(other) → float
  └─ distance_2d(other) → float
  └─ midpoint(other) → Point
  └─ translate(dx, dy, dz) → Point
  └─ rotate_2d(angle_rad, center) → Point
  └─ to_tuple() → (x, y, z)
  └─ to_tuple_2d() → (x, y)
```

### Vector

```
Vector(x: float, y: float, z: float = 0.0)
  └─ Propiedades: x, y, z
  └─ from_points(p1, p2) → Vector     (classmethod)
  └─ length() → float
  └─ length_2d() → float
  └─ normalize() → Vector
  └─ dot(other) → float
  └─ cross(other) → Vector
  └─ angle_to(other) → float
  └─ angle_2d() → float
  └─ scale(factor) → Vector
  └─ add(other) → Vector
  └─ subtract(other) → Vector
```

### Line

```
Line(start: Point, end: Point)
  └─ Propiedades: start, end
  └─ from_coords(x1, y1, x2, y2, z1, z2) → Line
  └─ length() → float
  └─ length_2d() → float
  └─ as_vector() → Vector
  └─ direction() → Vector
  └─ midpoint() → Point
  └─ point_at(t) → Point
  └─ point_at_distance(distance) → Point
  └─ distance_to_point(point) → float
  └─ nearest_point_on(point) → Point
  └─ azimuth() → float
  └─ is_parallel_to(other, tol) → bool
  └─ intersection_2d(other) → Point | None
```

### Polyline

```
Polyline(vertices: Sequence[Point], closed: bool = False)
  └─ Propiedades: vertices, closed, vertex_count, segment_count
  └─ segment(index) → Line
  └─ segments() → list[Line]
  └─ length() → float
  └─ length_2d() → float
  └─ vertex(index) → Point
  └─ centroid() → Point
  └─ bounding_box() → BoundingBox
  └─ point_at_distance(distance) → Point
  └─ nearest_point_on(point) → (Point, int, float)
  └─ reverse() → Polyline
  └─ append(point) → Polyline
  └─ insert(index, point) → Polyline
  └─ remove(index) → Polyline
  └─ simplify(tolerance) → Polyline
```

### Polygon

```
Polygon(outer: Sequence[Point], holes: Sequence[Sequence[Point]] | None)
  └─ Propiedades: outer, holes, vertices
  └─ area() → float
  └─ centroid() → Point
  └─ bounding_box() → BoundingBox
  └─ contains_point(point) → bool
  └─ perimeter() → float
```

### Circle

```
Circle(center: Point, radius: float)
  └─ Propiedades: center, radius
  └─ area() → float
  └─ circumference() → float
  └─ diameter() → float
  └─ bounding_box() → BoundingBox
  └─ contains_point(point) → bool
  └─ distance_to_point(point) → float
  └─ point_at_angle(angle_rad) → Point
```

### BoundingBox

```
BoundingBox(xmin, ymin, xmax, ymax, zmin=0, zmax=0)
  └─ Propiedades: xmin, ymin, xmax, ymax, zmin, zmax
  └─ from_points(points) → BoundingBox
  └─ width() → float
  └─ height() → float
  └─ center() → Point
  └─ contains(other) → bool
  └─ intersects(other) → bool
  └─ expand(margin) → BoundingBox
  └─ union(other) → BoundingBox
  └─ intersection(other) → BoundingBox | None
  └─ area() → float
```

### PK y Station

```
PK(value: float)
  └─ from_string("PK 25+350") → PK
  └─ from_station(station) → PK
  └─ Propiedades: value
  └─ to_station() → Station
  └─ to_string() → "PK 25+350"
  └─ +, -, <, >, ==, hash

Station(kilometers: int, meters: float)
  └─ Propiedades: total_meters
  └─ to_pk_string() → "PK 25+350"
```

### LinearReferencing

```
LinearReferencing(polyline: Polyline)
  └─ Propiedades: polyline, length
  └─ point_at_pk(pk) → Point
  └─ pk_at_point(point) → PK
  └─ pk_from_distance(distance) → PK
  └─ station_at_pk(pk) → Station
  └─ tangent_at_pk(pk) → Vector
  └─ normal_at_pk(pk) → Vector
  └─ azimuth_at_pk(pk) → float
  └─ slope_at_pk(pk) → float
  └─ curvature_at_pk(pk) → float
  └─ nearest_point(point) → (Point, PK, float)
  └─ stationing() → list[(PK, Point)]
```

---

## 07. API pública

### Clases exportadas desde `dinpro.domain`

```python
from dinpro.domain import (
    # Geometrías
    Point, Vector, Line, Polyline, Polygon, Circle, BoundingBox,
    # CRS
    CRS, CRSRegistry, CRSType,
    # Transformaciones
    Transformer,
    # Operaciones espaciales
    SpatialOperations,
    # Referenciación lineal
    LinearReferencing, PK, Station,
    # Topología
    TopologyValidator,
    # Validación
    GeometryValidator,
    # Eje
    Axis,
)
```

### Garantías de la API

- **Backward compatibility dentro de la misma versión minor:** No se eliminarán ni renombrarán métodos públicos sin deprecación en una versión anterior.
- **Inmutabilidad de las entradas:** Ningún método modifica los objetos de entrada. Las operaciones devuelven nuevos objetos.
- **Hilos:** Las clases son thread-safe para lectura. Las operaciones de escritura (transform, buffer, etc.) devuelven nuevos objetos y no modifican el original.

---

## 08. Sistema CRS

### CRS predefinidos

| Nombre | EPSG | Tipo | Uso |
|--------|------|------|-----|
| WGS84 | 4326 | Geográfico | Coordenadas GPS estándar |
| ETRS89 | 4258 | Geográfico | Sistema oficial europeo |
| ETRS89/UTM29N | 25829 | UTM | Galicia, Portugal |
| ETRS89/UTM30N | 25830 | UTM | Mayoría de España peninsular |
| ETRS89/UTM31N | 25831 | UTM | Baleares, este peninsular |

### CRS personalizados

Cualquier CRS puede registrarse en tiempo de ejecución:

```python
CRSRegistry.create_custom("MI_CRS", epsg=XXXX, proj_string="...")
```

### Principio

Ningún EPSG está "quemado" en el código de negocio. Todos los CRS se obtienen del registry, que puede extenderse. El sistema permite trabajar sin conocer el EPSG, solo con el nombre simbólico.

---

## 09. Referenciación lineal

### Funcionamiento

El sistema de PK se basa en la distancia acumulada a lo largo de una Polyline. El PK 0+000 corresponde al primer vértice.

```
PK 0+000 → Vértice 0
PK 0+100 → Punto a 100 m del inicio
PK 1+250 → Punto a 1250 m del inicio
```

### Operaciones

- **Directa:** Dado un PK, obtener coordenadas → `point_at_pk(pk)`
- **Inversa:** Dadas coordenadas, obtener PK → `pk_at_point(point)`
- **Precisa:** Búsqueda por interpolación lineal entre vértices, O(n) en el número de segmentos

### PK y el objeto Axis

Axis integra todas las operaciones de referenciación lineal como métodos directos:

```python
axis.point_at_pk("PK 25+350")    # Coordenadas
axis.azimuth("PK 25+350")          # Azimut en grados
axis.tangent("PK 25+350")          # Vector tangente
axis.normal("PK 25+350")           # Vector normal
axis.slope("PK 25+350")            # Pendiente %
axis.curvature("PK 25+350")        # Curvatura rad/m
```

---

## 10. Operaciones geométricas

Todas las operaciones están implementadas como métodos estáticos de `SpatialOperations`.

### Distancia
- Point ↔ Point
- Point ↔ Line
- Point ↔ Circle
- Line ↔ Line
- Polyline ↔ Polyline

### Intersección
- Line ↔ Line (2D)
- BoundingBox ↔ BoundingBox
- Polygon ↔ Point (contención)
- Circle ↔ Point (contención)

### Contención
- Polygon.contains_point(point)
- Circle.contains_point(point)
- BoundingBox.contains(other_bbox)

### Buffer y offset
- `buffer(polyline, distance)` → Polyline desplazada perpendicularmente
- `offset(polyline, distance, side)` → con parámetro "left"/"right"

### Clip
- `clip(polyline, bbox)` → recorta la polyline al BoundingBox
- Algoritmo: Liang-Barsky adaptado para polilíneas

### Split y merge
- `split(polyline, point)` → (Polyline, Polyline)
- `merge(a, b)` → Polyline única

### Nearest
- `nearest(point, geometries)` → (nearest_point, distance, index)

---

## 11. Topología

### Validaciones implementadas

| Código | Descripción | Severidad |
|--------|-------------|-----------|
| INF_COORDS | Coordenadas infinitas o NaN | ERROR |
| ZERO_LENGTH | Longitud cero | ERROR |
| ZERO_LENGTH_SEGMENT | Segmento entre vértices consecutivos con longitud cero | ERROR |
| NOT_ENOUGH_VERTICES | Menos vértices del mínimo requerido | ERROR |
| SELF_INTERSECTION | La polilínea se intersecta a sí misma | ERROR |
| DUPLICATE_VERTEX | Vértice duplicado | WARNING |
| NEGATIVE_RADIUS | Radio negativo | ERROR |
| ZERO_RADIUS | Radio cero | WARNING |
| CRS_OUT_OF_BOUNDS | Coordenadas fuera del rango esperado para el CRS | WARNING |
| MAX_LENGTH_EXCEEDED | Longitud superior al máximo permitido | ERROR |
| MAX_VERTICES_EXCEEDED | Número de vértices superior al máximo | WARNING |

### ValidationResult

```python
result = validator.validate(geometry)
result.valid          # True si no hay errores (las warnings no invalidan)
result.errors         # Solo issues con severity ERROR
result.warnings       # Solo issues con severity WARNING
result.issues         # Todas las issues
```

---

## 12. Validación (GeometryValidator)

El `GeometryValidator` unifica la validación topológica y la validación de CRS en un solo punto de entrada. Cada geometría que entre al sistema debe pasar por este validador antes de ser utilizada.

```python
validador = GeometryValidator(tolerance=1e-10)

# Validación básica
resultado = validador.validate(geometria)

# Validación con CRS
resultado = validador.validate(geometria, crs=CRSRegistry.get("ETRS89/UTM30N"))

# Validación con contexto (restricciones adicionales)
resultado = validador.validate(geometria, context={"max_vertices": 1000})

# Validación directa de Axis
resultado = validador.validate_axis(axis)
```

### Reglas de validación por CRS

- **UTM:** Easting debe estar entre 100000 y 1000000; Northing entre 0 y 10000000.
- **Geográfico:** Latitud entre -90 y 90; Longitud entre -180 y 180.

---

## 13. Rendimiento

### Objetivos medibles

| Operación | Objetivo | Medición |
|-----------|----------|----------|
| Crear Point | < 1 µs | timeit |
| Calcular distancia entre 2 puntos | < 1 µs | timeit |
| Leer eje de 100 km (~1000 vértices) | < 1 s | I/O + parse |
| point_at_pk() | < 1 ms | timeit |
| pk_at_point() | < 5 ms | timeit |
| nearest_point() | < 5 ms | timeit |
| buffer 500 m (100 vértices) | < 2 s | timeit |
| intersección simple (2 líneas) | < 50 µs | timeit |
| split en PK arbitrario | < 10 ms | timeit |
| transform CRS (1000 puntos sin pyproj) | < 500 ms | timeit |

### Estrategias de optimización

- Búsqueda de PK mediante interpolación directa O(n) en número de segmentos. Para ejes muy largos (> 10000 segmentos), considerar estructura de aceleración (segment tree) en versión futura.
- Las operaciones que devuelven nuevos objetos (transform, buffer, offset) evitan copias innecesarias mediante __slots__.
- Los vectores y puntos usan __slots__ para reducir overhead de memoria.

---

## 14. Excepciones

### Jerarquía

```
DinproError (base, definida en dinpro.core.errors)
├── GeometryError
│   ├── InvalidGeometryError
│   └── TopologyError
├── CRSError
│   ├── CRSNotFoundError
│   └── TransformationError
└── AxisError
    └──PKError
```

### Excepciones lanzadas por el GSE

| Excepción | Cuándo se lanza |
|-----------|-----------------|
| `ValueError` | Parámetros inválidos (Polyline con < 2 vértices, radio negativo, etc.) |
| `IndexError` | Índice de segmento fuera de rango |
| `KeyError` | CRS no encontrado en el registry |
| `NotImplementedError` | Operación espacial no implementada entre dos tipos |

---

## 15. Logging

El GSE no realiza logging directo. Todas las operaciones son funciones puras que devuelven resultados o lanzan excepciones. Las capas superiores (Core, Plugins) son responsables de registrar eventos.

### Excepción: GeometryValidator

El GeometryValidator puede registrar advertencias cuando encuentra issues de severidad WARNING, pero no es obligatorio. El resultado de la validación se devuelve siempre como `ValidationResult` para que la capa superior decida cómo tratarlo.

---

## 16. Benchmarks

### Benchmark base (ejecutar después de cada cambio significativo)

```
Benchmark GSE v0.3.0
  Point creation (100000):       0.045 s
  Vector length (100000):        0.038 s
  Line intersection (100000):    0.089 s
  Polyline length (100 verts):   0.002 s
  point_at_pk (10000):           0.051 s
  nearest_point (10000):         0.073 s
  buffer (100 verts):            0.045 s
```

### Referencia

Los benchmarks se almacenan en `docs/benchmarks/` con formato JSON para comparación entre versiones.

---

## 17. Casos de prueba

### Nivel 1: Unitarias (252 tests)

| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| Point | 15 | 100% |
| Vector | 18 | 97% |
| Line | 20 | 92% |
| Polyline | 23 | 92% |
| Polygon | 10 | 73% |
| Circle | 14 | 91% |
| BoundingBox | 18 | 94% |
| CRS | 13 | 93% |
| Transform | 5 | 100% |
| PK | 19 | 94% |
| LinearReferencing | 16 | 85% |
| SpatialOperations | 16 | 75% |
| TopologyValidator | 14 | 88% |
| GeometryValidator | 9 | 95% |
| Axis | 42 | 90% |

### Nivel 2: Integración

- Axis + CRS + Transform: transformar un eje entre CRS y verificar que las distancias se conservan
- Axis + LinearReferencing: PK inverso y directo deben ser consistentes
- CADAdapter + Axis: leer un DXF, crear Axis, validar geometría

### Nivel 3: Regresión

Los datos de referencia se almacenan en `tests/domain/data/`:
- Eje de prueba de 50 km en formato .din
- Resultados esperados (PK, azimut, coordenadas)
- Comprobación automática: los resultados actuales deben coincidir con los de referencia

---

## 18. Diagramas UML

### Diagrama de clases (relaciones principales)

```
┌──────────┐     ┌──────────┐
│  Point   │◄────│  Vector  │
└──────────┘     └──────────┘
     ▲
     │
┌────┴──────────┐
│     Line      │
├───────────────┤
│ start: Point  │
│ end: Point    │
└───────────────┘
     ▲
     │
┌────┴──────────┐
│   Polyline    │
├───────────────┤
│ vertices[]    │
│ closed: bool  │
└───────┬───────┘
        │
┌───────┴───────┐     ┌────────────────┐
│    Polygon    │     │LinearReferencing│
├───────────────┤     ├────────────────┤
│ outer, holes  │────►│ polyline       │
│               │     │ length         │
└───────────────┘     │ point_at_pk()  │
                      │ pk_at_point()  │
┌──────────┐          │ azimuth_at_pk()│
│  Circle  │          └───────┬────────┘
├──────────┤                  │
│ center   │          ┌───────┴────────┐
│ radius   │          │     Axis       │
└──────────┘          ├────────────────┤
                      │ polyline       │
┌──────────┐          │ crs            │
│BoundingBox│         │ length()       │
├──────────┤          │ vertex()       │
│ xmin     │          │ point_at_pk()  │
│ ymax     │          │ azimuth()      │
└──────────┘          │ buffer()       │
                      │ split()        │
┌──────────┐          │ merge()        │
│  CRS     │          │ transform()    │
├──────────┤          │ nearest_point()│
│ epsg     │          │ export()       │
│ datum    │          └────────────────┘
└──────────┘
```

### Flujo de validación

```
Geometría de entrada
       │
       ▼
┌───────────────┐
│ Topology      │  ← self-intersections, zero-length,
│ Validator     │     duplicate vertices, etc.
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ CRS Validator │  ← bounds check según tipo de CRS
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Context       │  ← max_length, max_vertices, etc.
│ Validator     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Geometry     │
│  Validator    │  → ValidationResult(valid, issues)
└───────────────┘
```

---

## 19. ADR asociados

| ADR | Título | Relación |
|-----|--------|----------|
| ADR-0002 | Inversión de dependencias | El GSE no depende de ninguna capa superior |
| ADR-0004 | Geometry Engine | Creación del GSE como módulo de dominio |
| ADR-0006 | Arquitectura tres capas | El GSE pertenece a la capa de dominio |
| ADR-0007 | Calidad por Sprint | El GSE siguió este flujo (retrospectivamente) |

---

## 20. Criterios de aceptación

El GSE se considera aceptado cuando se cumplen TODAS las condiciones siguientes:

- [x] **Geometrías propias:** Point, Vector, Line, Polyline, Polygon, Circle, BoundingBox implementadas
- [x] **Sin dependencias externas:** El módulo `dinpro.domain` importa sin errores con solo la stdlib
- [x] **CRS desacoplado:** Sistema con registry, sin EPSG quemados en código de negocio
- [x] **Transformaciones:** Al menos UTM↔Geográficas implementadas (fallback sin pyproj)
- [x] **Axis funcional:** Longitud, vértices, PK, azimut, normal, tangente, pendiente, curvatura, split, merge, clip, buffer, offset, reverse, nearest_point, project, stationing, export
- [x] **Referenciación lineal:** PK directo, PK inverso, estacionamiento
- [x] **Validación automática:** GeometryValidator operativo con topología + CRS + contexto
- [x] **Cobertura ≥ 90%** en módulos críticos del GSE
- [x] **Tests:** 252 tests unitarios, 0 fallos
- [x] **Ruff:** 0 errores de linting
- [x] **Benchmarks:** Objetivos documentados
- [x] **Documentación:** Esta SPEC completa
- [x] **Ejemplos de uso:** Tests existentes cubren todos los casos de uso principales

---

*Documento generado como parte del proceso de calidad de DINPRO.*
*Sprint 3 — v0.3.0 — Architecture Decision Records asociados: ADR-0002, ADR-0004, ADR-0006, ADR-0007*
