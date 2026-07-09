# Axis

Gestiona el eje de la infraestructura lineal.

## Responsabilidades

- Leer el eje desde un archivo (DXF, SHP, GPKG, CSV).
- Calcular longitud total.
- Calcular Puntos Kilométricos (PK).
- Obtener vértices del eje.
- Interpolar puntos sobre el eje.
- Buscar PK por coordenada o distancia.

## API Pública

```python
class Axis:
    def load(self, path: str) -> None
    def length(self) -> float
    def pk(self, point: tuple[float, float]) -> float
    def point(self, pk: float) -> tuple[float, float]
    def vertices(self) -> list[tuple[float, float]]
    def interpolate(self, t: float) -> tuple[float, float]
    def buffer(self, distance: float) -> Geometry
    def segment(self, start_pk: float, end_pk: float) -> Axis
    def closest_point(self, point: tuple[float, float]) -> tuple[float, float, float]
    @property
    def length(self) -> float
    @property
    def vertex_count(self) -> int
    @property
    def crs(self) -> str
```

## Dependencias

- Geometry (para buffer, intersecciones, bounding box)
- NUNCA depende de un módulo de negocio (carreteras, catastro, etc.)
