from __future__ import annotations

from typing import Sequence

from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point


class Polyline:
    def __init__(self, vertices: Sequence[Point], closed: bool = False) -> None:
        if len(vertices) < 2:
            raise ValueError("Polyline must have at least 2 vertices")
        self._vertices = list(vertices)
        self._closed = closed

    @classmethod
    def from_coords(
        cls, coords: Sequence[tuple[float, float, float]], closed: bool = False
    ) -> Polyline:
        return cls([Point(x, y, z) for x, y, z in coords], closed=closed)

    @classmethod
    def from_xy(cls, xy: Sequence[tuple[float, float]], closed: bool = False) -> Polyline:
        return cls([Point(x, y, 0.0) for x, y in xy], closed=closed)

    @property
    def vertices(self) -> list[Point]:
        return list(self._vertices)

    @property
    def closed(self) -> bool:
        return self._closed

    def vertex_count(self) -> int:
        return len(self._vertices)

    def segment_count(self) -> int:
        n = len(self._vertices)
        return n if self._closed else n - 1

    def segment(self, index: int) -> Line:
        n = len(self._vertices)
        if self._closed:
            i1 = index % n
            i2 = (index + 1) % n
        else:
            if index < 0 or index >= n - 1:
                raise IndexError(
                    f"Segment index {index} out of range for polyline with {n} vertices"
                )
            i1, i2 = index, index + 1
        return Line(self._vertices[i1], self._vertices[i2])

    def segments(self) -> list[Line]:
        n = len(self._vertices)
        result = []
        for i in range(self.segment_count()):
            i1 = i % n
            i2 = (i + 1) % n
            result.append(Line(self._vertices[i1], self._vertices[i2]))
        return result

    def length(self) -> float:
        return sum(seg.length() for seg in self.segments())

    def length_2d(self) -> float:
        return sum(seg.length_2d() for seg in self.segments())

    def vertex(self, index: int) -> Point:
        return self._vertices[index]

    def centroid(self) -> Point:
        cx = sum(p.x for p in self._vertices) / len(self._vertices)
        cy = sum(p.y for p in self._vertices) / len(self._vertices)
        cz = sum(p.z for p in self._vertices) / len(self._vertices)
        return Point(cx, cy, cz)

    def bounding_box(self) -> BoundingBox:
        from dinpro.domain.geometry.bounding_box import BoundingBox
        return BoundingBox.from_points(self._vertices)

    def point_at_distance(self, distance: float) -> Point:
        ln = self.length()
        if ln == 0.0:
            return self._vertices[0]
        d = abs(distance) % ln if self._closed else max(0.0, min(distance, ln))
        accumulated = 0.0
        for seg in self.segments():
            seg_len = seg.length()
            if accumulated + seg_len >= d:
                return seg.point_at_distance(d - accumulated)
            accumulated += seg_len
        return self._vertices[-1]

    def nearest_point_on(self, point: Point) -> tuple[Point, int, float]:
        best_point = self._vertices[0]
        best_seg = 0
        best_dist = float("inf")
        for i, seg in enumerate(self.segments()):
            np = seg.nearest_point_on(point)
            d = point.distance_to(np)
            if d < best_dist:
                best_dist = d
                best_point = np
                best_seg = i
        return best_point, best_seg, best_dist

    def reverse(self) -> Polyline:
        vertices = list(reversed(self._vertices))
        return Polyline(vertices, closed=self._closed)

    def append(self, point: Point) -> Polyline:
        return Polyline(self._vertices + [point], closed=self._closed)

    def insert(self, index: int, point: Point) -> Polyline:
        new_verts = list(self._vertices)
        new_verts.insert(index, point)
        return Polyline(new_verts, closed=self._closed)

    def remove(self, index: int) -> Polyline:
        new_verts = list(self._vertices)
        new_verts.pop(index)
        return Polyline(new_verts, closed=self._closed)

    def simplify(self, tolerance: float) -> Polyline:
        if len(self._vertices) <= 2:
            return self
        return Polyline._ramer_douglas_peucker(self._vertices, tolerance, closed=self._closed)

    @staticmethod
    def _ramer_douglas_peucker(
        points: list[Point], epsilon: float, closed: bool = False
    ) -> Polyline:
        if len(points) <= 2:
            return Polyline(points, closed=closed)
        dmax = 0.0
        idx = 0
        end = len(points) - 1
        line = Line(points[0], points[end])
        for i in range(1, end):
            d = line.distance_to_point(points[i])
            if d > dmax:
                dmax = d
                idx = i
        if dmax > epsilon:
            left = Polyline._ramer_douglas_peucker(points[: idx + 1], epsilon, closed=False)
            right = Polyline._ramer_douglas_peucker(points[idx:], epsilon, closed=False)
            result = Polyline(left._vertices[:-1] + right._vertices, closed=closed)
            return result
        else:
            return Polyline([points[0], points[-1]], closed=closed)

    def to_coords(self) -> list[tuple[float, float, float]]:
        return [p.to_tuple() for p in self._vertices]

    def to_coords_2d(self) -> list[tuple[float, float]]:
        return [p.to_tuple_2d() for p in self._vertices]

    def __repr__(self) -> str:
        return f"Polyline({len(self._vertices)} vertices, closed={self._closed})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Polyline):
            return NotImplemented
        return self._vertices == other._vertices and self._closed == other._closed

    def __hash__(self) -> int:
        return hash((tuple(self._vertices), self._closed))

