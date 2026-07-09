from __future__ import annotations

import math
from typing import Sequence

from dinpro.domain.geometry.point import Point


class BoundingBox:
    __slots__ = ("_xmin", "_ymin", "_xmax", "_ymax", "_zmin", "_zmax")

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float,
                 zmin: float = 0.0, zmax: float = 0.0) -> None:
        if xmin > xmax or ymin > ymax:
            raise ValueError("min values must be <= max values")
        self._xmin = float(xmin)
        self._ymin = float(ymin)
        self._xmax = float(xmax)
        self._ymax = float(ymax)
        self._zmin = float(zmin)
        self._zmax = float(zmax)

    @classmethod
    def from_points(cls, points: Sequence[Point]) -> BoundingBox:
        if not points:
            raise ValueError("At least one point needed")
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        zs = [p.z for p in points]
        return cls(min(xs), min(ys), max(xs), max(ys), min(zs), max(zs))

    @property
    def xmin(self) -> float:
        return self._xmin

    @property
    def ymin(self) -> float:
        return self._ymin

    @property
    def xmax(self) -> float:
        return self._xmax

    @property
    def ymax(self) -> float:
        return self._ymax

    @property
    def zmin(self) -> float:
        return self._zmin

    @property
    def zmax(self) -> float:
        return self._zmax

    def width(self) -> float:
        return self._xmax - self._xmin

    def height(self) -> float:
        return self._ymax - self._ymin

    def depth(self) -> float:
        return self._zmax - self._zmin

    def center(self) -> Point:
        return Point(
            (self._xmin + self._xmax) / 2.0,
            (self._ymin + self._ymax) / 2.0,
            (self._zmin + self._zmax) / 2.0,
        )

    def contains(self, other: BoundingBox) -> bool:
        return (
            self._xmin <= other._xmin and self._xmax >= other._xmax
            and self._ymin <= other._ymin and self._ymax >= other._ymax
            and self._zmin <= other._zmin and self._zmax >= other._zmax
        )

    def intersects(self, other: BoundingBox) -> bool:
        return not (
            self._xmax < other._xmin or self._xmin > other._xmax
            or self._ymax < other._ymin or self._ymin > other._ymax
        )

    def expand(self, margin: float) -> BoundingBox:
        return BoundingBox(
            self._xmin - margin, self._ymin - margin,
            self._xmax + margin, self._ymax + margin,
            self._zmin, self._zmax,
        )

    def union(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            min(self._xmin, other._xmin), min(self._ymin, other._ymin),
            max(self._xmax, other._xmax), max(self._ymax, other._ymax),
            min(self._zmin, other._zmin), max(self._zmax, other._zmax),
        )

    def intersection(self, other: BoundingBox) -> BoundingBox | None:
        xmin = max(self._xmin, other._xmin)
        ymin = max(self._ymin, other._ymin)
        xmax = min(self._xmax, other._xmax)
        ymax = min(self._ymax, other._ymax)
        if xmin > xmax or ymin > ymax:
            return None
        return BoundingBox(xmin, ymin, xmax, ymax)

    def area(self) -> float:
        return self.width() * self.height()

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self._xmin, self._ymin, self._xmax, self._ymax)

    def __repr__(self) -> str:
        return (
            f"BoundingBox({self._xmin:.4f}, {self._ymin:.4f}, "
            f"{self._xmax:.4f}, {self._ymax:.4f})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BoundingBox):
            return NotImplemented
        return (
            math.isclose(self._xmin, other._xmin)
            and math.isclose(self._ymin, other._ymin)
            and math.isclose(self._xmax, other._xmax)
            and math.isclose(self._ymax, other._ymax)
        )

    def __hash__(self) -> int:
        return hash((round(self._xmin, 10), round(self._ymin, 10),
                     round(self._xmax, 10), round(self._ymax, 10)))
