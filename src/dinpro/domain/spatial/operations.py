from __future__ import annotations

import math
from typing import Sequence

from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.geometry.circle import Circle
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.geometry.vector import Vector


class SpatialOperations:
    @staticmethod
    def distance(a: Point | Line | Polyline | Polygon | Circle,
                 b: Point | Line | Polyline | Polygon | Circle) -> float:
        if isinstance(a, Point) and isinstance(b, Point):
            return a.distance_to(b)
        if isinstance(a, Point) and isinstance(b, Line):
            return b.distance_to_point(a)
        if isinstance(a, Line) and isinstance(b, Point):
            return a.distance_to_point(b)
        if isinstance(a, Point) and isinstance(b, Circle):
            return b.distance_to_point(a)
        if isinstance(a, Circle) and isinstance(b, Point):
            return a.distance_to_point(b)
        if isinstance(a, Polyline) and isinstance(b, Polyline):
            return SpatialOperations._polyline_distance(a, b)
        if isinstance(a, Polyline) and isinstance(b, Point):
            _, _, d = a.nearest_point_on(b)
            return d
        if isinstance(a, Point) and isinstance(b, Polyline):
            _, _, d = b.nearest_point_on(a)
            return d
        return SpatialOperations._generic_distance(a, b)

    @staticmethod
    def intersects(a: Point | Line | Polyline | Polygon | Circle | BoundingBox,
                   b: Point | Line | Polyline | Polygon | Circle | BoundingBox) -> bool:
        if isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
            return a.intersects(b)
        if isinstance(a, Polygon) and isinstance(b, Point):
            return a.contains_point(b)
        if isinstance(a, Point) and isinstance(b, Polygon):
            return b.contains_point(a)
        if isinstance(a, Circle) and isinstance(b, Point):
            return a.contains_point(b)
        if isinstance(a, Point) and isinstance(b, Circle):
            return b.contains_point(a)
        if isinstance(a, Line) and isinstance(b, Line):
            return a.intersection_2d(b) is not None
        return SpatialOperations._generic_intersects(a, b)

    @staticmethod
    def contains(a: Polygon | Circle | BoundingBox,
                 b: Point | Polygon | Circle | BoundingBox) -> bool:
        if isinstance(a, Polygon) and isinstance(b, Point):
            return a.contains_point(b)
        if isinstance(a, Circle) and isinstance(b, Point):
            return a.contains_point(b)
        if isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
            return a.contains(b)
        return SpatialOperations._generic_contains(a, b)

    @staticmethod
    def within(a: Point | Polygon | Circle | BoundingBox,
               b: Polygon | Circle | BoundingBox) -> bool:
        return SpatialOperations.contains(b, a)

    @staticmethod
    def nearest(a: Point, geometry: Sequence[Point | Line | Polyline]) -> tuple[Point, float, int]:
        best_point = Point(0, 0)
        best_dist = float("inf")
        best_idx = 0
        for i, geom in enumerate(geometry):
            if isinstance(geom, Point):
                d = a.distance_to(geom)
                np = geom
            elif isinstance(geom, Line):
                np = geom.nearest_point_on(a)
                d = a.distance_to(np)
            elif isinstance(geom, Polyline):
                np, _, d = geom.nearest_point_on(a)
            else:
                continue
            if d < best_dist:
                best_dist = d
                best_point = np
                best_idx = i
        return best_point, best_dist, best_idx

    @staticmethod
    def buffer(polyline: Polyline, distance: float) -> Polyline:
        if distance == 0.0:
            return polyline
        verts = polyline.vertices
        if len(verts) < 2:
            return polyline
        offset_verts: list[Point] = []
        for i in range(len(verts)):
            angle = SpatialOperations._vertex_bisector(verts, i)
            normal_angle = angle + math.pi / 2.0
            dx = distance * math.cos(normal_angle)
            dy = distance * math.sin(normal_angle)
            offset_verts.append(Point(verts[i].x + dx, verts[i].y + dy, verts[i].z))
        return Polyline(offset_verts, closed=polyline.closed)

    @staticmethod
    def offset(polyline: Polyline, distance: float, side: str = "left") -> Polyline:
        sign = 1.0 if side == "left" else -1.0
        return SpatialOperations.buffer(polyline, distance * sign)

    @staticmethod
    def clip(polyline: Polyline, bbox: BoundingBox) -> Polyline:
        verts = polyline.vertices
        clipped = []
        for i in range(len(verts) - 1):
            seg = Line(verts[i], verts[i + 1])
            if bbox.contains(BoundingBox.from_points([seg.start, seg.end])):
                clipped.append(seg.start)
                if i == len(verts) - 2:
                    clipped.append(seg.end)
            else:
                t_start = SpatialOperations._clip_segment(seg, bbox)
                if t_start is not None and t_start[0] is not None:
                    if not clipped or clipped[-1] != t_start[0]:
                        clipped.append(t_start[0])
                    if t_start[1] is not None:
                        clipped.append(t_start[1])
        if polyline.closed and len(verts) > 2:
            seg = Line(verts[-1], verts[0])
            if bbox.contains(BoundingBox.from_points([seg.start, seg.end])):
                if not clipped or clipped[-1] != seg.start:
                    clipped.append(seg.start)
            else:
                t = SpatialOperations._clip_segment(seg, bbox)
                if t is not None and t[0] is not None:
                    if not clipped or clipped[-1] != t[0]:
                        clipped.append(t[0])
                    if t[1] is not None:
                        clipped.append(t[1])
        if len(clipped) < 2:
            return Polyline.from_xy([(0, 0), (0, 0)])
        return Polyline(clipped, closed=polyline.closed)

    @staticmethod
    def split(polyline: Polyline, point: Point) -> tuple[Polyline, Polyline]:
        np, seg_idx, _ = polyline.nearest_point_on(point)
        verts = polyline.vertices
        seg = Line(verts[seg_idx], verts[seg_idx + 1])
        v = seg.as_vector()
        dot_vv = v.dot(v)
        if dot_vv == 0.0:
            t = 0.0
        else:
            vp = Vector.from_points(seg.start, np)
            t = max(0.0, min(1.0, v.dot(vp) / dot_vv))
        split_point = seg.point_at(t)
        left_verts = verts[: seg_idx + 1] + [split_point]
        right_verts = [split_point] + verts[seg_idx + 1:]
        return Polyline(left_verts, closed=False), Polyline(right_verts, closed=False)

    @staticmethod
    def merge(a: Polyline, b: Polyline) -> Polyline:
        if a.vertices[-1].distance_to(b.vertices[0]) < 1e-10:
            return Polyline(a.vertices + b.vertices[1:], closed=False)
        if a.vertices[-1].distance_to(b.vertices[-1]) < 1e-10:
            return Polyline(a.vertices + list(reversed(b.vertices[:-1])), closed=False)
        if a.vertices[0].distance_to(b.vertices[0]) < 1e-10:
            return Polyline(list(reversed(a.vertices[:-1])) + b.vertices, closed=False)
        if a.vertices[0].distance_to(b.vertices[-1]) < 1e-10:
            return Polyline(b.vertices + a.vertices[1:], closed=False)
        return Polyline(a.vertices + b.vertices, closed=False)

    @staticmethod
    def touches(a: Polyline | Polygon, b: Polyline | Polygon) -> bool:
        return SpatialOperations.distance(a, b) < 1e-10

    @staticmethod
    def _generic_distance(a: object, b: object) -> float:
        if isinstance(a, Line) and isinstance(b, Line):
            return SpatialOperations._line_distance(a, b)
        raise NotImplementedError(
            f"Distance between {type(a).__name__} and {type(b).__name__}"
            " not implemented"
        )

    @staticmethod
    def _line_distance(a: Line, b: Line) -> float:
        d1 = a.distance_to_point(b.start)
        d2 = a.distance_to_point(b.end)
        d3 = b.distance_to_point(a.start)
        d4 = b.distance_to_point(a.end)
        return min(d1, d2, d3, d4)

    @staticmethod
    def _polyline_distance(a: Polyline, b: Polyline) -> float:
        min_dist = float("inf")
        for seg_a in a.segments():
            for seg_b in b.segments():
                d = SpatialOperations.distance(seg_a, seg_b)
                if d < min_dist:
                    min_dist = d
                    if min_dist == 0.0:
                        return 0.0
        return min_dist

    @staticmethod
    def _generic_intersects(a: object, b: object) -> bool:
        raise NotImplementedError(
            f"Intersection check between {type(a).__name__}"
            f" and {type(b).__name__} not implemented"
        )

    @staticmethod
    def _generic_contains(a: object, b: object) -> bool:
        raise NotImplementedError(
            f"Contains check between {type(a).__name__}"
            f" and {type(b).__name__} not implemented"
        )

    @staticmethod
    def _vertex_bisector(verts: list[Point], i: int) -> float:
        n = len(verts)
        p0 = verts[(i - 1) % n]
        p1 = verts[i]
        p2 = verts[(i + 1) % n]
        a1 = math.atan2(p1.y - p0.y, p1.x - p0.x)
        a2 = math.atan2(p2.y - p1.y, p2.x - p1.x)
        return (a1 + a2) / 2.0

    @staticmethod
    def _clip_segment(seg: Line, bbox: BoundingBox) -> tuple[Point | None, Point | None]:
        dx = seg.end.x - seg.start.x
        dy = seg.end.y - seg.start.y
        t0 = 0.0
        t1 = 1.0
        for edge in range(4):
            if edge == 0:
                if dx != 0.0:
                    t = (bbox.xmin - seg.start.x) / dx
                    if dx < 0:
                        t1 = min(t1, t)
                    else:
                        t0 = max(t0, t)
            elif edge == 1:
                if dx != 0.0:
                    t = (bbox.xmax - seg.start.x) / dx
                    if dx > 0:
                        t1 = min(t1, t)
                    else:
                        t0 = max(t0, t)
            elif edge == 2:
                if dy != 0.0:
                    t = (bbox.ymin - seg.start.y) / dy
                    if dy < 0:
                        t1 = min(t1, t)
                    else:
                        t0 = max(t0, t)
            elif edge == 3:
                if dy != 0.0:
                    t = (bbox.ymax - seg.start.y) / dy
                    if dy > 0:
                        t1 = min(t1, t)
                    else:
                        t0 = max(t0, t)

        if t0 > t1:
            return (None, None)

        p_start = seg.point_at(min(max(t0, 0.0), 1.0)) if t0 > 0.0 else None
        p_end = seg.point_at(min(max(t1, 0.0), 1.0)) if t1 < 1.0 else None
        return (p_start, p_end)

    @staticmethod
    def _distance_to_vertex(polyline: Polyline, idx: int) -> float:
        d = 0.0
        for i in range(idx):
            d += Line(polyline.vertices[i], polyline.vertices[i + 1]).length()
        return d
