from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.polyline import Polyline

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.linear_referencing.station import Station


def _extract_subpolyline(
    polyline: Polyline,
    dist_start: float,
    dist_end: float,
) -> Polyline:
    if dist_start >= dist_end:
        raise ValueError("dist_start must be less than dist_end")
    total = polyline.length()
    if dist_start < 0:
        dist_start = 0.0
    if dist_end > total:
        dist_end = total
    if dist_start >= dist_end:
        raise ValueError("No valid sub-polyline in range")
    segments = polyline.segments()
    cum: float = 0.0
    seg_starts: list[float] = [0.0]
    for seg in segments:
        cum += seg.length()
        seg_starts.append(cum)
    pts: list[Point] = []
    for i, seg in enumerate(segments):
        s = seg_starts[i]
        e = seg_starts[i + 1]
        if e <= dist_start or s >= dist_end:
            continue
        if s < dist_start and not pts:
            pts.append(seg.point_at_distance(dist_start - s))
        if not pts:
            pts.append(seg.start)
        mid_end = min(e, dist_end)
        if math.isclose(mid_end, e, rel_tol=1e-12):
            pts.append(seg.end)
        else:
            pts.append(seg.point_at_distance(mid_end - s))
    if len(pts) < 2:
        raise ValueError("Sub-polyline too short")
    return Polyline(pts)


@dataclass(frozen=True)
class Segment:
    _axis: Axis = field(repr=False)
    _start: Station
    _end: Station
    _geometry: Polyline = field(repr=False, compare=False)
    _attributes: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
    _metadata: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
    _id: str = field(default="", repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._start.value >= self._end.value:
            raise ValueError("Segment start must be before end")
        if not self._id:
            object.__setattr__(self, "_id", uuid.uuid4().hex[:12])

    @property
    def id(self) -> str:
        return self._id

    @property
    def axis(self) -> Axis:
        return self._axis

    @property
    def station_start(self) -> Station:
        return self._start

    @property
    def station_end(self) -> Station:
        return self._end

    @property
    def geometry(self) -> Polyline:
        return self._geometry

    @property
    def length(self) -> float:
        return self._geometry.length()

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self._attributes)

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def reverse(self) -> Segment:
        rev_geom = Polyline(self._geometry.reverse().vertices)
        return Segment(
            _axis=self._axis,
            _start=self._start,
            _end=self._end,
            _geometry=rev_geom,
            _attributes=self._attributes,
            _metadata=self._metadata,
        )

    def contains(self, station: Station) -> bool:
        val = station.value
        return self._start.value <= val <= self._end.value

    def intersects(self, other: Segment) -> bool:
        return (
            self._axis == other._axis
            and self._start.value < other._end.value
            and other._start.value < self._end.value
        )

    def to_axis(self) -> Axis:
        from dinpro.domain.axis import Axis as _Axis
        return _Axis(
            polyline=self._geometry,
            crs=self._axis.crs,
            name=f"{self._axis.name}_{self._start.value:.0f}_{self._end.value:.0f}",
        )

    def offset(
        self,
        distance: float,
        steps: int = 50,
    ) -> Polygon:
        from dinpro.domain.lateral.lateral_projection import LateralProjection
        lp = LateralProjection(self._axis)
        return lp.corridor(
            pk_start=self._start.value,
            pk_end=self._end.value,
            half_width=abs(distance),
            steps=steps,
        )

    def clip(
        self,
        start: Station,
        end: Station,
    ) -> Segment:
        from dinpro.domain.linear_referencing.station import Station as _Station
        new_start = _Station(max(start.value, self._start.value))
        new_end = _Station(min(end.value, self._end.value))
        if new_start.value >= new_end.value:
            raise ValueError("Clipped segment would have zero length")
        new_geom = _extract_subpolyline(
            self._axis.polyline, new_start.value, new_end.value
        )
        return Segment(
            _axis=self._axis,
            _start=new_start,
            _end=new_end,
            _geometry=new_geom,
            _attributes=self._attributes,
            _metadata=self._metadata,
        )

    def __repr__(self) -> str:
        return f"Segment({self._start.value:.3f} - {self._end.value:.3f}, len={self.length:.3f})"
