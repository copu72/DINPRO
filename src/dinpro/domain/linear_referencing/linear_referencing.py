from __future__ import annotations

import math

from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.geometry.vector import Vector
from dinpro.domain.linear_referencing.pk import PK, Station


class LinearReferencing:
    def __init__(self, polyline: Polyline) -> None:
        if polyline.vertex_count() < 2:
            raise ValueError("Polyline must have at least 2 vertices")
        self._polyline = polyline
        self._length = polyline.length()

    @property
    def polyline(self) -> Polyline:
        return self._polyline

    @property
    def length(self) -> float:
        return self._length

    def point_at_pk(self, pk: PK) -> Point:
        d = pk.value
        return self._polyline.point_at_distance(d)

    def pk_at_point(self, point: Point) -> PK:
        _, seg_idx, dist = self._polyline.nearest_point_on(point)
        accumulated = 0.0
        for i in range(seg_idx):
            accumulated += Line(
                self._polyline.vertices[i], self._polyline.vertices[i + 1]
            ).length()
        seg = self._polyline.segment(seg_idx)
        seg_point = seg.nearest_point_on(point)
        accumulated += seg.start.distance_to(seg_point)
        return PK(accumulated)

    def pk_from_distance(self, distance: float) -> PK:
        return PK(distance)

    def station_at_pk(self, pk: PK) -> Station:
        return pk.to_station()

    def tangent_at_pk(self, pk: PK) -> Vector:
        point = self._polyline.point_at_distance(pk.value)
        _, seg_idx, _ = self._polyline.nearest_point_on(point)
        seg = self._polyline.segment(seg_idx)
        return seg.direction()

    def normal_at_pk(self, pk: PK) -> Vector:
        tangent = self.tangent_at_pk(pk)
        return Vector(-tangent.y, tangent.x, 0.0).normalize()

    def azimuth_at_pk(self, pk: PK) -> float:
        tangent = self.tangent_at_pk(pk)
        az = math.degrees(tangent.angle_2d())
        return az % 360.0

    def slope_at_pk(self, pk: PK) -> float:
        point = self._polyline.point_at_distance(pk.value)
        _, seg_idx, _ = self._polyline.nearest_point_on(point)
        seg = self._polyline.segment(seg_idx)
        if seg.length_2d() == 0:
            return 0.0
        dz = seg.end.z - seg.start.z
        return math.degrees(math.atan2(dz, seg.length_2d()))

    def curvature_at_pk(self, pk: PK) -> float:
        point = self._polyline.point_at_distance(pk.value)
        _, seg_idx, _ = self._polyline.nearest_point_on(point)
        if seg_idx == 0 or seg_idx >= self._polyline.segment_count() - 1:
            return 0.0
        p0 = self._polyline.vertices[seg_idx - 1]
        p1 = self._polyline.vertices[seg_idx]
        p2 = self._polyline.vertices[seg_idx + 1]
        v1 = Vector.from_points(p0, p1)
        v2 = Vector.from_points(p1, p2)
        angle = v1.angle_to(v2)
        avg_len = (v1.length() + v2.length()) / 2.0
        if avg_len == 0:
            return 0.0
        return angle / avg_len

    def point_at_distance(self, distance: float) -> Point:
        return self._polyline.point_at_distance(distance)

    def nearest_point(self, point: Point) -> tuple[Point, PK, float]:
        np, seg_idx, dist = self._polyline.nearest_point_on(point)
        pk = self.pk_at_point(np)
        return np, pk, dist

    def project(self, point: Point) -> tuple[Point, PK, float]:
        return self.nearest_point(point)

    def stationing(self) -> list[tuple[PK, Point]]:
        stations: list[tuple[PK, Point]] = []
        accumulated = 0.0
        verts = self._polyline.vertices
        stations.append((PK(0.0), verts[0]))
        for i in range(len(verts) - 1):
            seg_len = verts[i].distance_to(verts[i + 1])
            accumulated += seg_len
            stations.append((PK(accumulated), verts[i + 1]))
        return stations

    def segment_at_pk(self, pk: PK) -> Line:
        _, seg_idx, _ = self._polyline.nearest_point_on(
            self._polyline.point_at_distance(pk.value)
        )
        return self._polyline.segment(seg_idx)
