from __future__ import annotations

import math


class Point:
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

    def distance_to(self, other: Point) -> float:
        dx = self._x - other._x
        dy = self._y - other._y
        dz = self._z - other._z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def distance_2d(self, other: Point) -> float:
        dx = self._x - other._x
        dy = self._y - other._y
        return math.sqrt(dx * dx + dy * dy)

    def midpoint(self, other: Point) -> Point:
        return Point(
            (self._x + other._x) / 2.0,
            (self._y + other._y) / 2.0,
            (self._z + other._z) / 2.0,
        )

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Point:
        return Point(self._x + dx, self._y + dy, self._z + dz)

    def rotate_2d(self, angle_rad: float, center: Point | None = None) -> Point:
        cx = center._x if center else 0.0
        cy = center._y if center else 0.0
        rx = cx + (self._x - cx) * math.cos(angle_rad) - (self._y - cy) * math.sin(angle_rad)
        ry = cy + (self._x - cx) * math.sin(angle_rad) + (self._y - cy) * math.cos(angle_rad)
        return Point(rx, ry, self._z)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def to_tuple_2d(self) -> tuple[float, float]:
        return (self._x, self._y)

    def __repr__(self) -> str:
        return f"Point({self._x:.4f}, {self._y:.4f}, {self._z:.4f})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (
            math.isclose(self._x, other._x)
            and math.isclose(self._y, other._y)
            and math.isclose(self._z, other._z)
        )

    def __hash__(self) -> int:
        return hash((round(self._x, 10), round(self._y, 10), round(self._z, 10)))
