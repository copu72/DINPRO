from __future__ import annotations

import math

from dinpro.domain.geometry.point import Point


class Vector:
    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: float, y: float, z: float = 0.0) -> None:
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> Vector:
        return cls(p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)

    def length(self) -> float:
        return math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    def length_2d(self) -> float:
        return math.sqrt(self._x * self._x + self._y * self._y)

    def normalize(self) -> Vector:
        ln = self.length()
        if ln == 0.0:
            return Vector(0.0, 0.0, 0.0)
        return Vector(self._x / ln, self._y / ln, self._z / ln)

    def dot(self, other: Vector) -> float:
        return self._x * other._x + self._y * other._y + self._z * other._z

    def cross(self, other: Vector) -> Vector:
        return Vector(
            self._y * other._z - self._z * other._y,
            self._z * other._x - self._x * other._z,
            self._x * other._y - self._y * other._x,
        )

    def angle_to(self, other: Vector) -> float:
        dot = self.dot(other)
        ln = self.length() * other.length()
        if ln == 0.0:
            return 0.0
        cos_a = max(-1.0, min(1.0, dot / ln))
        return math.acos(cos_a)

    def angle_2d(self) -> float:
        return math.atan2(self._y, self._x)

    def scale(self, factor: float) -> Vector:
        return Vector(self._x * factor, self._y * factor, self._z * factor)

    def add(self, other: Vector) -> Vector:
        return Vector(self._x + other._x, self._y + other._y, self._z + other._z)

    def subtract(self, other: Vector) -> Vector:
        return Vector(self._x - other._x, self._y - other._y, self._z - other._z)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def __repr__(self) -> str:
        return f"Vector({self._x:.4f}, {self._y:.4f}, {self._z:.4f})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (
            math.isclose(self._x, other._x)
            and math.isclose(self._y, other._y)
            and math.isclose(self._z, other._z)
        )

    def __hash__(self) -> int:
        return hash((round(self._x, 10), round(self._y, 10), round(self._z, 10)))
