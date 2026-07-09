import math
from typing import Any

from dinpro.core.errors import GeometryError


class Geometry:
    @staticmethod
    def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def angle(p1: tuple[float, float], p2: tuple[float, float]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.atan2(dy, dx)

    @staticmethod
    def azimuth(p1: tuple[float, float], p2: tuple[float, float]) -> float:
        rad = Geometry.angle(p1, p2)
        deg = math.degrees(rad)
        return (deg + 360) % 360

    @staticmethod
    def bounding_box(
        points: list[tuple[float, float]],
    ) -> tuple[float, float, float, float]:
        if not points:
            raise GeometryError("Cannot compute bounding box of empty point list")
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return (min(xs), min(ys), max(xs), max(ys))

    @staticmethod
    def length(geom: Any) -> float:
        if isinstance(geom, list):
            if len(geom) < 2:
                return 0.0
            total = 0.0
            for i in range(len(geom) - 1):
                total += Geometry.distance(geom[i], geom[i + 1])
            return total
        raise GeometryError(f"Cannot compute length for type: {type(geom)}")

    @staticmethod
    def area(geom: Any) -> float:
        if isinstance(geom, list):
            if len(geom) < 3:
                return 0.0
            n = len(geom)
            a = 0.0
            for i in range(n):
                j = (i + 1) % n
                a += geom[i][0] * geom[j][1]
                a -= geom[j][0] * geom[i][1]
            return abs(a) / 2.0
        raise GeometryError(f"Cannot compute area for type: {type(geom)}")

    @staticmethod
    def interpolate(
        line: list[tuple[float, float]], t: float
    ) -> tuple[float, float]:
        if len(line) < 2:
            raise GeometryError("Need at least 2 points for interpolation")
        total_length = Geometry.length(line)
        target = total_length * t
        accumulated = 0.0
        for i in range(len(line) - 1):
            seg_len = Geometry.distance(line[i], line[i + 1])
            if accumulated + seg_len >= target or i == len(line) - 2:
                local_t = (target - accumulated) / seg_len if seg_len > 0 else 0
                x = line[i][0] + local_t * (line[i + 1][0] - line[i][0])
                y = line[i][1] + local_t * (line[i + 1][1] - line[i][1])
                return (x, y)
            accumulated += seg_len
        return line[-1]

    @staticmethod
    def closest_point_on_line(
        point: tuple[float, float],
        line_start: tuple[float, float],
        line_end: tuple[float, float],
    ) -> tuple[float, float, float]:
        sx, sy = line_start
        ex, ey = line_end
        px, py = point
        dx = ex - sx
        dy = ey - sy
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            dist = Geometry.distance(point, line_start)
            return (sx, sy, dist)
        t = ((px - sx) * dx + (py - sy) * dy) / length_sq
        t = max(0.0, min(1.0, t))
        cx = sx + t * dx
        cy = sy + t * dy
        dist = Geometry.distance(point, (cx, cy))
        return (cx, cy, dist)
