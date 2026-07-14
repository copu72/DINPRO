from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.linear_referencing.measure_system import MeasureSystem
    from dinpro.domain.linear_referencing.station import Station


class LateralProjection:
    def __init__(
        self,
        axis: Axis,
        measure_system: MeasureSystem | None = None,
    ) -> None:
        if axis.vertex_count < 2:
            raise ValueError("Axis must have at least 2 vertices")
        self._axis = axis
        self._measure_system = measure_system

    def offset_point(
        self,
        pk: float | str | Station | None = None,
        distance: float = 1.0,
        side: str = "left",
    ) -> Point:
        pk_val = self._resolve_pk_value(pk)
        if distance == 0.0:
            return self._axis.point_at_pk(pk_val)
        normal = self._axis.normal(pk_val)
        factor = distance if side == "left" else -distance
        center = self._axis.point_at_pk(pk_val)
        return Point(
            center.x + normal.x * factor,
            center.y + normal.y * factor,
            center.z,
        )

    def cross_section(
        self,
        pk: float | str | Station | None = None,
        left_width: float = 10.0,
        right_width: float = 10.0,
    ) -> dict[str, Any]:
        pk_val = self._resolve_pk_value(pk)
        center = self._axis.point_at_pk(pk_val)
        normal = self._axis.normal(pk_val)
        left = Point(
            center.x + normal.x * left_width,
            center.y + normal.y * left_width,
            center.z,
        )
        right = Point(
            center.x - normal.x * right_width,
            center.y - normal.y * right_width,
            center.z,
        )
        return {
            "center": center,
            "left": left,
            "right": right,
            "pk": pk_val,
            "azimuth": self._axis.azimuth(pk_val),
        }

    def cross_section_line(
        self,
        pk: float | str | Station | None = None,
        left_width: float = 10.0,
        right_width: float = 10.0,
    ) -> tuple[Point, Point]:
        cs = self.cross_section(pk, left_width, right_width)
        return (cs["left"], cs["right"])

    def corridor(
        self,
        pk_start: float | str | Station | None = None,
        pk_end: float | str | Station | None = None,
        half_width: float = 25.0,
        steps: int = 100,
    ) -> Polygon:
        start_val = self._resolve_pk_value(pk_start)
        end_val = self._resolve_pk_value(pk_end)
        length = end_val - start_val
        if length <= 0:
            raise ValueError("pk_end must be greater than pk_start")
        step_size = length / steps

        left_points: list[Point] = []
        right_points: list[Point] = []

        for i in range(steps + 1):
            current = start_val + i * step_size
            center = self._axis.point_at_pk(current)
            normal = self._axis.normal(current)
            left_points.append(
                Point(
                    center.x + normal.x * half_width,
                    center.y + normal.y * half_width,
                    center.z,
                )
            )
            right_points.append(
                Point(
                    center.x - normal.x * half_width,
                    center.y - normal.y * half_width,
                    center.z,
                )
            )

        vertices = left_points + right_points[::-1]
        return Polygon(vertices)

    def corridor_vertices(
        self,
        pk_start: float | str | Station | None = None,
        pk_end: float | str | Station | None = None,
        half_width: float = 25.0,
        steps: int = 100,
    ) -> dict[str, list[Point]]:
        start_val = self._resolve_pk_value(pk_start)
        end_val = self._resolve_pk_value(pk_end)
        length = end_val - start_val
        if length <= 0:
            raise ValueError("pk_end must be greater than pk_start")
        step_size = length / steps

        left: list[Point] = []
        right: list[Point] = []
        centerline: list[Point] = []

        for i in range(steps + 1):
            current = start_val + i * step_size
            center = self._axis.point_at_pk(current)
            normal = self._axis.normal(current)
            centerline.append(center)
            left.append(
                Point(
                    center.x + normal.x * half_width,
                    center.y + normal.y * half_width,
                    center.z,
                )
            )
            right.append(
                Point(
                    center.x - normal.x * half_width,
                    center.y - normal.y * half_width,
                    center.z,
                )
            )

        return {"center": centerline, "left": left, "right": right}

    def margins(
        self,
        pk: float | str | Station | None = None,
    ) -> dict[str, Point]:
        return self.cross_section(pk, left_width=0.0, right_width=0.0)

    def nearest_pk(self, point: Point) -> tuple[float, float]:
        _, pk, distance = self._axis.nearest_point(point)
        return (pk.value, distance)

    def project_to_axis(
        self, point: Point
    ) -> dict[str, Any]:
        nearest, pk, distance = self._axis.nearest_point(point)
        return {
            "point": nearest,
            "pk": pk.value,
            "distance": distance,
            "azimuth": self._axis.azimuth(pk),
            "side": self._determine_side(point, nearest, pk),
        }

    def _determine_side(
        self, point: Point, nearest: Point, pk: Any
    ) -> str:
        normal = self._axis.normal(pk)
        dx = point.x - nearest.x
        dy = point.y - nearest.y
        dot = dx * normal.x + dy * normal.y
        return "left" if dot >= 0 else "right"

    def _resolve_pk_value(
        self, pk: float | str | Station | None
    ) -> float:
        from dinpro.domain.linear_referencing.station import Station as _Station
        if pk is None:
            return 0.0
        if isinstance(pk, _Station):
            return pk.value
        if isinstance(pk, str):
            return _Station.parse(pk).value
        return float(pk)

    @property
    def axis(self) -> Axis:
        return self._axis
