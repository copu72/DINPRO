# EPIC-002 — Spatial Query Engine API

**Versión:** 0.1
**Estado:** Preliminar

---

## 1. IndexedFeature

```python
@dataclass(frozen=True)
class IndexedFeature:
    geometry: Geometry       # Polygon | Polyline | Point
    properties: dict         # Metadatos arbitrarios (ej: {"name": "Madrid", "type": "municipality"})
    id: str = ""             # Identificador único opcional
```

## 2. LinearIntersection

```python
@dataclass(frozen=True)
class LinearIntersection:
    feature: IndexedFeature   # La geometría que intersecta
    entry_pk: float           # PK de entrada sobre el eje
    exit_pk: float            # PK de salida sobre el eje
    entry_point: Point        # Punto de entrada en coordenadas
    exit_point: Point         # Punto de salida en coordenadas

    @property
    def affected_length(self) -> float:
        return self.exit_pk - self.entry_pk
```

## 3. SpatialQueryEngine

```python
class SpatialQueryEngine:
    """Motor de consultas espaciales referenciadas al eje lineal."""

    def __init__(
        self,
        axis: Axis,
        lateral: LateralProjection | None = None,
    ) -> None:
        ...

    # --- Indexado ---

    def index(self, features: list[IndexedFeature]) -> None:
        """Indexa una colección de geometrías externas.
        
        Las geometrías se almacenan para consultas posteriores.
        Reemplaza el índice actual si se llama de nuevo.
        """

    def index_from_geometries(
        self,
        geometries: list[Geometry],
        properties: list[dict] | None = None,
    ) -> None:
        """Indexa geometrías sin envolver en IndexedFeature."""

    # --- Consultas ---

    def intersect_axis(self) -> list[LinearIntersection]:
        """Encuentra todas las geometrías indexadas que intersectan el eje.
        
        Returns:
            Lista de intersecciones ordenadas por entry_pk ascendente.
        """

    def intersect_corridor(
        self,
        half_width: float = 25.0,
        steps: int = 100,
    ) -> list[LinearIntersection]:
        """Encuentra geometrías que intersectan el corredor del eje.
        
        Args:
            half_width: Semiancho del corredor en metros.
            steps: Pasos de discretización del eje.
        
        Returns:
            Intersecciones ordenadas por entry_pk.
        """

    def intersect_range(
        self,
        pk_start: float = 0.0,
        pk_end: float | None = None,
        half_width: float = 0.0,
    ) -> list[LinearIntersection]:
        """Encuentra geometrías que intersectan un rango de PK del eje.
        
        Args:
            pk_start: PK inicial del rango.
            pk_end: PK final (None = hasta el final del eje).
            half_width: 0 = solo eje, >0 = corredor.
        
        Returns:
            Intersecciones dentro del rango, ordenadas por entry_pk.
        """

    # --- Utilidades ---

    def count(self) -> int:
        """Número de geometrías indexadas."""

    def get_by_id(self, feature_id: str) -> IndexedFeature | None:
        """Recupera una geometría indexada por su ID."""

    def clear(self) -> None:
        """Elimina todas las geometrías indexadas."""

    # --- Generación de eventos ---

    def to_events(
        self,
        intersections: list[LinearIntersection],
        event_type: str = "intersection",
    ) -> list[LinearEvent]:
        """Convierte intersecciones en eventos lineales.
        
        Cada intersección genera un LinearEvent con:
        - pk_start = entry_pk
        - pk_end = exit_pk
        - properties heredados de IndexedFeature.properties
        """
```

## 4. Flujo de uso típico

```python
# 1. Crear el motor
sqe = SpatialQueryEngine(axis=axis, lateral=LateralProjection(axis))

# 2. Indexar geometrías externas
sqe.index([
    IndexedFeature(geometry=madrid_polygon, properties={"name": "Madrid", "type": "municipality"}),
    IndexedFeature(geometry=road_polyline, properties={"name": "A-3", "type": "road"}),
])

# 3. Consultar intersecciones
results = sqe.intersect_corridor(half_width=50.0)

# 4. Convertir a eventos
events = sqe.to_events(results)

# 5. Iterar
for r in results:
    print(f"{r.entry_pk:.3f} - {r.exit_pk:.3f}: {r.feature.properties['name']} ({r.affected_length:.1f} m)")
```

## 5. Interfaces internas (no expuestas en la API pública)

```python
class _SpatialScanner:
    """Escaneo lineal: recorre el eje y detecta intersecciones con geometrías indexadas."""
    def scan(self, axis: Axis, corridor: Polygon | None = None) -> list[LinearIntersection]: ...

class _IntersectionDetector:
    """Detección de puntos de entrada/salida entre geometrías."""
    def detect(self, axis_geom: Geometry, target: Geometry) -> list[tuple[float, float]]: ...
```
