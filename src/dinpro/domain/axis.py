from __future__ import annotations

from typing import Any

from dinpro.domain.crs.crs import CRS
from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline as GeomPolyline
from dinpro.domain.geometry.vector import Vector
from dinpro.domain.linear_referencing.linear_referencing import LinearReferencing
from dinpro.domain.linear_referencing.pk import PK
from dinpro.domain.spatial.operations import SpatialOperations
from dinpro.domain.transform.transformer import Transformer


class Axis:
    def __init__(self, polyline: GeomPolyline, crs: CRS | None = None,
                 name: str = "") -> None:
        self._polyline = polyline
        self._crs = crs
        self._name = name
        self._linear = LinearReferencing(polyline)
        self._transformer = Transformer()

    @classmethod
    def from_coords(cls, coords: list[tuple[float, float, float]],
                    crs: CRS | None = None, name: str = "",
                    closed: bool = False) -> Axis:
        return cls(GeomPolyline.from_coords(coords, closed=closed), crs=crs, name=name)

    @classmethod
    def from_xy(cls, xy: list[tuple[float, float]],
                crs: CRS | None = None, name: str = "") -> Axis:
        return cls(GeomPolyline.from_xy(xy), crs=crs, name=name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def crs(self) -> CRS | None:
        return self._crs

    @property
    def polyline(self) -> GeomPolyline:
        return self._polyline

    @property
    def vertices(self) -> list[Point]:
        return self._polyline.vertices

    def vertex(self, index: int) -> Point:
        return self._polyline.vertex(index)

    @property
    def length(self) -> float:
        return self._polyline.length()

    @property
    def length_2d(self) -> float:
        return self._polyline.length_2d()

    @property
    def vertex_count(self) -> int:
        return self._polyline.vertex_count()

    @property
    def closed(self) -> bool:
        return self._polyline.closed

    def segments(self) -> list[Line]:
        return self._polyline.segments()

    def segment(self, index: int) -> Line:
        return self._polyline.segment(index)

    def bounding_box(self) -> BoundingBox:
        return self._polyline.bounding_box()

    def centroid(self) -> Point:
        return self._polyline.centroid()

    def point_at(self, distance: float) -> Point:
        return self._linear.point_at_distance(distance)

    def point_at_pk(self, pk: PK | str | float) -> Point:
        if isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.point_at_pk(pk)

    def pk_at_point(self, point: Point) -> PK:
        return self._linear.pk_at_point(point)

    def pk_from_distance(self, distance: float) -> PK:
        return PK(distance)

    def pk(self, value: float | str | None = None) -> PK:
        if value is None:
            return PK(0.0)
        if isinstance(value, str):
            return PK.from_string(value)
        return PK(float(value))

    def stationing(self) -> list[tuple[PK, Point]]:
        return self._linear.stationing()

    def azimuth(self, pk: PK | str | float | None = None) -> float:
        if pk is None:
            pk = PK(0.0)
        elif isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.azimuth_at_pk(pk)

    def tangent(self, pk: PK | str | float | None = None) -> Vector:
        if pk is None:
            pk = PK(0.0)
        elif isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.tangent_at_pk(pk)

    def normal(self, pk: PK | str | float | None = None) -> Vector:
        if pk is None:
            pk = PK(0.0)
        elif isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.normal_at_pk(pk)

    def slope(self, pk: PK | str | float | None = None) -> float:
        if pk is None:
            pk = PK(0.0)
        elif isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.slope_at_pk(pk)

    def curvature(self, pk: PK | str | float | None = None) -> float:
        if pk is None:
            pk = PK(0.0)
        elif isinstance(pk, str):
            pk = PK.from_string(pk)
        elif isinstance(pk, (int, float)):
            pk = PK(float(pk))
        return self._linear.curvature_at_pk(pk)

    def nearest_point(self, point: Point) -> tuple[Point, PK, float]:
        return self._linear.nearest_point(point)

    def project(self, point: Point) -> tuple[Point, PK, float]:
        return self._linear.project(point)

    def buffer(self, distance: float) -> Axis:
        new_poly = SpatialOperations.buffer(self._polyline, distance)
        return Axis(new_poly, crs=self._crs, name=f"{self._name}_buffer")

    def offset(self, distance: float, side: str = "left") -> Axis:
        new_poly = SpatialOperations.offset(self._polyline, distance, side)
        return Axis(new_poly, crs=self._crs, name=f"{self._name}_offset")

    def split(self, point: Point) -> tuple[Axis, Axis]:
        left_poly, right_poly = SpatialOperations.split(self._polyline, point)
        return (
            Axis(left_poly, crs=self._crs, name=f"{self._name}_left"),
            Axis(right_poly, crs=self._crs, name=f"{self._name}_right"),
        )

    def split_at_pk(self, pk: PK | str | float) -> tuple[Axis, Axis]:
        point = self.point_at_pk(pk)
        return self.split(point)

    def merge(self, other: Axis) -> Axis:
        new_poly = SpatialOperations.merge(self._polyline, other._polyline)
        return Axis(new_poly, crs=self._crs or other._crs, name=f"{self._name}_merged")

    def clip(self, bbox: BoundingBox) -> Axis:
        new_poly = SpatialOperations.clip(self._polyline, bbox)
        return Axis(new_poly, crs=self._crs, name=f"{self._name}_clipped")

    def reverse(self) -> Axis:
        return Axis(self._polyline.reverse(), crs=self._crs, name=f"{self._name}_rev")

    def simplify(self, tolerance: float) -> Axis:
        return Axis(self._polyline.simplify(tolerance), crs=self._crs, name=f"{self._name}_simp")

    def transform(self, target_crs: CRS) -> Axis:
        if self._crs is None:
            raise ValueError("Axis has no CRS defined")
        new_verts = []
        for v in self._polyline.vertices:
            result = self._transformer.transform(v, self._crs, target_crs)
            if not result.success:
                raise ValueError(f"Transformation failed: {result.error}")
            new_verts.append(result.point)
        new_poly = GeomPolyline(new_verts, closed=self._polyline.closed)
        return Axis(new_poly, crs=target_crs, name=self._name)

    def export(self, format: str = "dict") -> Any:
        if format == "dict":
            return {
                "name": self._name,
                "crs": self._crs.name if self._crs else None,
                "vertices": [v.to_tuple() for v in self._polyline.vertices],
                "closed": self._polyline.closed,
                "length": self._polyline.length(),
            }
        if format == "coords":
            return self._polyline.to_coords()
        if format == "coords_2d":
            return self._polyline.to_coords_2d()
        raise ValueError(f"Unsupported export format: {format}")

    def __repr__(self) -> str:
        vc = self._polyline.vertex_count()
        return f"Axis('{self._name}', {vc} vertices, length={self._polyline.length():.2f})"
