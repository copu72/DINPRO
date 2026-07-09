from __future__ import annotations

from typing import Sequence

from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline


class Polygon:
    def __init__(
        self, outer: Sequence[Point],
        holes: Sequence[Sequence[Point]] | None = None,
    ) -> None:
        if len(outer) < 3:
            raise ValueError("Polygon outer ring must have at least 3 vertices")
        self._outer = Polyline(outer, closed=True)
        self._holes: list[Polyline] = []
        if holes:
            for h in holes:
                if len(h) >= 3:
                    self._holes.append(Polyline(h, closed=True))

    @classmethod
    def from_coords(cls, outer: Sequence[tuple[float, float, float]],
                    holes: Sequence[Sequence[tuple[float, float, float]]] | None = None) -> Polygon:
        return cls([Point(x, y, z) for x, y, z in outer],
                   holes=[[Point(x, y, z) for x, y, z in h] for h in holes] if holes else None)

    @classmethod
    def from_xy(cls, outer: Sequence[tuple[float, float]],
                holes: Sequence[Sequence[tuple[float, float]]] | None = None) -> Polygon:
        return cls([Point(x, y, 0.0) for x, y in outer],
                   holes=[[Point(x, y, 0.0) for x, y in h] for h in holes] if holes else None)

    @property
    def outer(self) -> Polyline:
        return self._outer

    @property
    def holes(self) -> list[Polyline]:
        return list(self._holes)

    @property
    def vertices(self) -> list[Point]:
        return self._outer.vertices

    def area(self) -> float:
        return abs(self._signed_area()) - sum(abs(h._signed_area()) for h in self._holes)

    def _signed_area(self) -> float:
        verts = self._outer.vertices
        n = len(verts)
        a = 0.0
        for i in range(n):
            j = (i + 1) % n
            a += verts[i].x * verts[j].y
            a -= verts[j].x * verts[i].y
        return a / 2.0

    def centroid(self) -> Point:
        cx = sum(p.x for p in self._outer._vertices) / len(self._outer._vertices)
        cy = sum(p.y for p in self._outer._vertices) / len(self._outer._vertices)
        cz = sum(p.z for p in self._outer._vertices) / len(self._outer._vertices)
        return Point(cx, cy, cz)

    def bounding_box(self) -> BoundingBox:
        return BoundingBox.from_points(self._outer._vertices)

    def contains_point(self, point: Point) -> bool:
        verts = self._outer._vertices
        n = len(verts)
        inside = False
        j = n - 1
        for i in range(n):
            yi = verts[i].y
            yj = verts[j].y
            xi = verts[i].x
            xj = verts[j].x
            if ((yi > point.y) != (yj > point.y)) and \
               (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        if inside and self._holes:
            for h in self._holes:
                if self._point_in_ring(h._vertices, point):
                    return False
        return inside

    @staticmethod
    def _point_in_ring(verts: list[Point], point: Point) -> bool:
        n = len(verts)
        inside = False
        j = n - 1
        for i in range(n):
            yi = verts[i].y
            yj = verts[j].y
            xi = verts[i].x
            xj = verts[j].x
            if ((yi > point.y) != (yj > point.y)) and \
               (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def perimeter(self) -> float:
        return self._outer.length()

    def to_coords(self) -> list[tuple[float, float, float]]:
        return self._outer.to_coords()

    def to_coords_2d(self) -> list[tuple[float, float]]:
        return self._outer.to_coords_2d()

    def __repr__(self) -> str:
        return f"Polygon({len(self._outer._vertices)} vertices, {len(self._holes)} holes)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polygon):
            return NotImplemented
        return self._outer == other._outer and self._holes == other._holes


