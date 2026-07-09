from __future__ import annotations

import math

from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.geometry.point import Point


class Circle:
    __slots__ = ("_center", "_radius")

    def __init__(self, center: Point, radius: float) -> None:
        if radius < 0.0:
            raise ValueError("Radius must be non-negative")
        self._center = center
        self._radius = float(radius)

    @classmethod
    def from_coords(cls, x: float, y: float, radius: float, z: float = 0.0) -> Circle:
        return cls(Point(x, y, z), radius)

    @property
    def center(self) -> Point:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    def area(self) -> float:
        return math.pi * self._radius * self._radius

    def circumference(self) -> float:
        return 2.0 * math.pi * self._radius

    def diameter(self) -> float:
        return 2.0 * self._radius

    def bounding_box(self) -> BoundingBox:


        return BoundingBox(
            self._center.x - self._radius,
            self._center.y - self._radius,
            self._center.x + self._radius,
            self._center.y + self._radius,
        )

    def contains_point(self, point: Point) -> bool:
        return self._center.distance_2d(point) <= self._radius + 1e-12

    def distance_to_point(self, point: Point) -> float:
        d = self._center.distance_to(point)
        return max(0.0, d - self._radius)

    def point_at_angle(self, angle_rad: float) -> Point:
        return Point(
            self._center.x + self._radius * math.cos(angle_rad),
            self._center.y + self._radius * math.sin(angle_rad),
            self._center.z,
        )

    def to_tuple(self) -> tuple[tuple[float, float, float], float]:
        return (self._center.to_tuple(), self._radius)

    def __repr__(self) -> str:
        return f"Circle(center={self._center!r}, radius={self._radius:.4f})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self._center == other._center and math.isclose(self._radius, other._radius)

    def __hash__(self) -> int:
        return hash((self._center, round(self._radius, 10)))


