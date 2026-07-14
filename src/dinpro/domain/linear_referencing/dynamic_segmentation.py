from __future__ import annotations

from typing import TYPE_CHECKING

from dinpro.domain.linear_referencing.segment import Segment, _extract_subpolyline

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.linear_referencing.station import Station


class DynamicSegmentation:
    def __init__(self, axis: Axis) -> None:
        self._axis = axis

    def segment(
        self,
        start: Station,
        end: Station,
    ) -> Segment:
        if start.value >= end.value:
            raise ValueError("start must be before end")
        geometry = _extract_subpolyline(
            self._axis.polyline, start.value, end.value
        )
        return Segment(
            _axis=self._axis,
            _start=start,
            _end=end,
            _geometry=geometry,
        )

    def split(
        self,
        stations: list[Station],
    ) -> list[Segment]:
        if not stations:
            return [self._full_segment()]
        sorted_stations = sorted(stations, key=lambda s: s.value)
        result: list[Segment] = []
        prev: Station | None = None
        axis_length = self._axis.length
        for s in sorted_stations:
            if s.value <= 0 or s.value >= axis_length:
                continue
            if prev is None:
                if s.value > 0:
                    start_geom = _extract_subpolyline(self._axis.polyline, 0.0, s.value)
                    result.append(
                        Segment(
                            _axis=self._axis,
                            _start=self._make_station(0.0),
                            _end=s,
                            _geometry=start_geom,
                        )
                    )
            else:
                geom = _extract_subpolyline(self._axis.polyline, prev.value, s.value)
                result.append(
                    Segment(
                        _axis=self._axis,
                        _start=prev,
                        _end=s,
                        _geometry=geom,
                    )
                )
            prev = s
        if prev is not None and prev.value < axis_length:
            end_geom = _extract_subpolyline(self._axis.polyline, prev.value, axis_length)
            result.append(
                Segment(
                    _axis=self._axis,
                    _start=prev,
                    _end=self._make_station(axis_length),
                    _geometry=end_geom,
                )
            )
        if not result:
            return [self._full_segment()]
        return result

    @staticmethod
    def merge(segments: list[Segment]) -> Segment:
        if not segments:
            raise ValueError("Cannot merge empty list")
        first = segments[0]
        min_start = first.station_start.value
        max_end = first.station_end.value
        axis = first.axis
        for seg in segments[1:]:
            if seg.axis != axis:
                raise ValueError("All segments must belong to the same axis")
            min_start = min(min_start, seg.station_start.value)
            max_end = max(max_end, seg.station_end.value)
        if min_start >= max_end:
            raise ValueError("Merged segment would have zero length")
        geometry = _extract_subpolyline(axis.polyline, min_start, max_end)
        return Segment(
            _axis=axis,
            _start=first.station_start.__class__(min_start),
            _end=first.station_start.__class__(max_end),
            _geometry=geometry,
        )

    def _full_segment(self) -> Segment:
        from dinpro.domain.linear_referencing.station import Station as _Station
        axis_length = self._axis.length
        geometry = _extract_subpolyline(self._axis.polyline, 0.0, axis_length)
        return Segment(
            _axis=self._axis,
            _start=_Station(0.0),
            _end=_Station(axis_length),
            _geometry=geometry,
        )

    @staticmethod
    def _make_station(value: float) -> Station:
        from dinpro.domain.linear_referencing.station import Station as _Station
        return _Station(value)

    @property
    def axis(self) -> Axis:
        return self._axis
