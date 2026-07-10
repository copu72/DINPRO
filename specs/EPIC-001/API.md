# EPIC-001: Linear Referencing Engine

## API — Interfaz pública

---

### MeasureSystem

```python
class MeasureSystem:
    def __init__(self, axis: Axis, calibrations: list[CalibrationPoint] | None = None)
    def pk_at_distance(self, distance: float) -> float
    def distance_at_pk(self, pk: float) -> float
    def calibrate(self, points: list[CalibrationPoint]) -> None
    def add_discontinuity(self, pk: float, gap: float) -> None
    def total_measure(self) -> float
```

### AdvancedStationing

```python
class AdvancedStationing:
    def __init__(self, axis: Axis, measure_system: MeasureSystem | None = None)
    def point_at_pk(self, pk: PK | str | float) -> Point
    def pk_at_point(self, point: Point) -> PK
    def nearest_pk(self, point: Point) -> tuple[Point, PK, float]
    def format_pk(self, pk: PK, format: str = "default") -> str
    def set_precision(self, decimals: int) -> None
    def set_output_format(self, fmt: str) -> None
```

### LateralProjection

```python
class LateralProjection:
    def __init__(self, axis: Axis)
    def offset_point(self, pk: PK | str | float, distance: float, side: str = "left") -> Point
    def offset_points(self, pk_start: PK, pk_end: PK, distance: float, side: str = "left", step: float = 20.0) -> list[tuple[PK, Point]]
    def cross_section(self, pk: PK | str | float, width: float) -> tuple[Point, Point]
    def left(self, pk: PK | str | float, distance: float) -> Point
    def right(self, pk: PK | str | float, distance: float) -> Point
```

### DynamicSegmentation

```python
class DynamicSegmentation:
    def __init__(self, axis: Axis)
    def split_by_events(self, events: list[LinearEvent]) -> list[LinearSegment]
    def merge_segments(self, segments: list[LinearSegment]) -> list[LinearSegment]
    def clip(self, pk_start: PK, pk_end: PK) -> Polyline
    def intersection(self, a: LinearSegment, b: LinearSegment) -> LinearSegment | None
    def contains(self, outer: LinearSegment, inner: LinearSegment) -> bool
```

### LinearEvent

```python
class LinearEvent:
    event_id: str
    event_type: str
    pk_start: PK
    pk_end: PK
    attributes: dict
    version: int
    revision: str
    created_at: str
    updated_at: str

class LinearEventSet:
    def __init__(self, events: list[LinearEvent] | None = None)
    def add(self, event: LinearEvent) -> None
    def remove(self, event_id: str) -> None
    def update(self, event_id: str, attributes: dict) -> LinearEvent
    def query(self, pk: PK) -> list[LinearEvent]
    def query_range(self, pk_start: PK, pk_end: PK) -> list[LinearEvent]
    def overlaps(self) -> list[tuple[LinearEvent, LinearEvent]]
    def gaps(self) -> list[LinearSegment]
    def audit_trail(self, event_id: str) -> list[LinearEvent]
```

### RouteCalibration

```python
class RouteCalibration:
    def __init__(self, axis: Axis)
    def auto_calibrate(self, known_points: list[tuple[PK, Point]]) -> MeasureSystem
    def adjust_pk(self, pk: PK, offset: float) -> PK
    def reset_pk(self, new_start_pk: PK) -> MeasureSystem
    def validate_calibration(self, measure_system: MeasureSystem) -> list[str]
```

### LongitudinalProfile

```python
class LongitudinalProfile:
    def __init__(self, axis: Axis)
    def profile(self, step: float = 20.0) -> list[ProfilePoint]
    def slope_segments(self, tolerance: float = 0.5) -> list[LinearSegment]
    def maximum_slope(self) -> tuple[PK, float]
    def critical_points(self) -> list[ProfilePoint]
    def accumulated_climb(self) -> float
```

### LREExporter

```python
class LREExporter:
    def __init__(self, axis: Axis)
    def to_csv(self, events: list[LinearEvent], path: str) -> None
    def to_geojson(self, events: list[LinearEvent], path: str) -> None
    def to_excel(self, events: list[LinearEvent], path: str) -> None
```
