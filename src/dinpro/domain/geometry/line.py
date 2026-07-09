from __future__ import annotations

import math

from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.vector import Vector


class Line:
    __slots__ = ("_start", "_end")

    def __init__(self, start: Point, end: Point) -> None:
        self._start = start
        self._end = end

    @classmethod
    def from_coords(
        cls, x1: float, y1: float, x2: float, y2: float,
        z1: float = 0.0, z2: float = 0.0,
    ) -> Line:
        return cls(Point(x1, y1, z1), Point(x2, y2, z2))

    @property
    def start(self) -> Point:
        return self._start

    @property
    def end(self) -> Point:
        return self._end

    def length(self) -> float:
        return self._start.distance_to(self._end)

    def length_2d(self) -> float:
        return self._start.distance_2d(self._end)

    def as_vector(self) -> Vector:
        return Vector.from_points(self._start, self._end)

    def direction(self) -> Vector:
        return self.as_vector().normalize()

    def midpoint(self) -> Point:
        return self._start.midpoint(self._end)

    def point_at(self, t: float) -> Point:
        v = self.as_vector()
        return Point(
            self._start.x + v.x * t,
            self._start.y + v.y * t,
            self._start.z + v.z * t,
        )

    def point_at_distance(self, distance: float) -> Point:
        ln = self.length()
        if ln == 0.0:
            return self._start
        return self.point_at(distance / ln)

    def distance_to_point(self, point: Point) -> float:
        v = self.as_vector()
        vp = Vector.from_points(self._start, point)
        t = v.dot(vp) / v.dot(v)
        t = max(0.0, min(1.0, t))
        proj = self.point_at(t)
        return point.distance_to(proj)

    def nearest_point_on(self, point: Point) -> Point:
        v = self.as_vector()
        vp = Vector.from_points(self._start, point)
        dot_vv = v.dot(v)
        if dot_vv == 0.0:
            return self._start
        t = v.dot(vp) / dot_vv
        t = max(0.0, min(1.0, t))
        return self.point_at(t)

    def azimuth(self) -> float:
        dx = self._end.x - self._start.x
        dy = self._end.y - self._start.y
        return math.atan2(dy, dx)

    def is_parallel_to(self, other: Line, tol: float = 1e-10) -> bool:
        v1 = self.as_vector()
        v2 = other.as_vector()
        cross_z = v1.x * v2.y - v1.y * v2.x
        return abs(cross_z) < tol

    def intersection_2d(self, other: Line) -> Point | None:
        x1, y1 = self._start.x, self._start.y
        x2, y2 = self._end.x, self._end.y
        x3, y3 = other._start.x, other._start.y
        x4, y4 = other._end.x, other._end.y
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-12:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Point(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        return None

    def to_tuple(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        return (self._start.to_tuple(), self._end.to_tuple())

    def __repr__(self) -> str:
        return f"Line({self._start!r}, {self._end!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Line):
            return NotImplemented
        return self._start == other._start and self._end == other._end

    def __hash__(self) -> int:
        return hash((self._start, self._end))
