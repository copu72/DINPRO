# Geometry

Operaciones espaciales básicas del Core.

## Responsabilidades

- Cálculos geométricos fundamentales.
- Sistema de coordenadas.
- Buffer, intersecciones, bounding box.
- Transformaciones espaciales.

## API Pública

```python
class Geometry:
    @staticmethod
    def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float
    @staticmethod
    def angle(p1: tuple[float, float], p2: tuple[float, float]) -> float
    @staticmethod
    def azimuth(p1: tuple[float, float], p2: tuple[float, float]) -> float
    @staticmethod
    def buffer(geom, distance: float) -> Geometry
    @staticmethod
    def intersection(geom1, geom2) -> Geometry | None
    @staticmethod
    def bounding_box(points: list[tuple[float, float]]) -> tuple[float, float, float, float]
    @staticmethod
    def transform(geom, from_crs: str, to_crs: str) -> Geometry
    @staticmethod
    def length(geom) -> float
    @staticmethod
    def area(geom) -> float
```

## Notas

- Geometry es puramente funcional (stateless).
- No conoce Axis, Project ni ningún módulo.
- Es la única dependencia espacial del Core.
