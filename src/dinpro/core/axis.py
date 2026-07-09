from typing import Any

from dinpro.core.errors import AxisError
from dinpro.core.geometry import Geometry


class Axis:
    def __init__(self) -> None:
        self._vertices: list[tuple[float, float]] = []
        self._crs: str = "EPSG:25830"
        self._metadata: dict[str, Any] = {}

    def load(self, vertices: list[tuple[float, float]], crs: str = "EPSG:25830") -> None:
        if len(vertices) < 2:
            raise AxisError("Axis must have at least 2 vertices")
        self._vertices = list(vertices)
        self._crs = crs

    def length(self) -> float:
        return Geometry.length(self._vertices)

    def pk(self, point: tuple[float, float]) -> float:
        if len(self._vertices) < 2:
            raise AxisError("Cannot compute PK: axis has fewer than 2 vertices")
        min_dist = float("inf")
        closest_pk = 0.0
        accumulated = 0.0
        for i in range(len(self._vertices) - 1):
            _, _, dist = Geometry.closest_point_on_line(
                point, self._vertices[i], self._vertices[i + 1]
            )
            seg_len = Geometry.distance(self._vertices[i], self._vertices[i + 1])
            if dist < min_dist:
                min_dist = dist
                closest_pk = accumulated + Geometry.distance(
                    self._vertices[i],
                    Geometry.closest_point_on_line(
                        point, self._vertices[i], self._vertices[i + 1]
                    )[:2],
                )
            accumulated += seg_len
        return closest_pk

    def point(self, pk: float) -> tuple[float, float]:
        total = self.length()
        if pk < 0 or pk > total:
            raise AxisError(f"PK {pk} is outside axis range [0, {total}]")
        t = pk / total if total > 0 else 0
        return Geometry.interpolate(self._vertices, t)

    def vertices(self) -> list[tuple[float, float]]:
        return list(self._vertices)

    def interpolate(self, t: float) -> tuple[float, float]:
        return Geometry.interpolate(self._vertices, t)

    def closest_point(self, point: tuple[float, float]) -> tuple[float, float, float]:
        min_dist = float("inf")
        closest = (0.0, 0.0, 0.0)
        for i in range(len(self._vertices) - 1):
            result = Geometry.closest_point_on_line(
                point, self._vertices[i], self._vertices[i + 1]
            )
            if result[2] < min_dist:
                min_dist = result[2]
                closest = result
        return closest

    def clear(self) -> None:
        self._vertices = []
        self._metadata = {}

    @property
    def vertex_count(self) -> int:
        return len(self._vertices)

    @property
    def crs(self) -> str:
        return self._crs

    @crs.setter
    def crs(self, value: str) -> None:
        self._crs = value
