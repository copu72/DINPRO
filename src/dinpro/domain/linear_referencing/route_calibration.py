from __future__ import annotations

import bisect
from typing import TYPE_CHECKING, Sequence

from dinpro.domain.linear_referencing.extrapolation_mode import ExtrapolationMode

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.linear_referencing.calibration_issue import CalibrationIssue
    from dinpro.domain.linear_referencing.calibration_set import CalibrationSet
    from dinpro.domain.linear_referencing.station import Station


class CalibrationError(ValueError):
    pass


class RouteCalibration:
    def __init__(
        self,
        axis: Axis,
        calibration_sets: Sequence[CalibrationSet],
        default_campaign: str | None = None,
    ) -> None:
        if not calibration_sets:
            raise ValueError("At least one CalibrationSet is required")
        self._axis = axis
        self._sets: dict[str, CalibrationSet] = {cs.campaign_id: cs for cs in calibration_sets}
        self._default_campaign = default_campaign or calibration_sets[0].campaign_id
        if self._default_campaign not in self._sets:
            raise ValueError(
                f"default_campaign '{self._default_campaign}' not found in calibration_sets"
            )

    @property
    def axis(self) -> Axis:
        return self._axis

    @property
    def calibration_sets(self) -> list[CalibrationSet]:
        return list(self._sets.values())

    @property
    def active_set(self) -> CalibrationSet:
        return self._sets[self._default_campaign]

    def station_at_distance(
        self,
        distance: float,
        mode: ExtrapolationMode = ExtrapolationMode.NONE,
    ) -> Station:
        pts = self.active_set.points
        if not pts:
            raise CalibrationError("No calibration points available")
        d0 = getattr(pts[0], "_distance", 0.0)
        dn = getattr(pts[-1], "_distance", 0.0)
        if distance < d0 or distance > dn:
            return self._extrapolate_station(distance, pts, d0, dn, mode)
        i = bisect.bisect_right([getattr(p, "_distance", 0.0) for p in pts], distance) - 1
        if i < 0:
            i = 0
        if i >= len(pts) - 1:
            i = len(pts) - 2
        return self._interpolate_station(pts[i], pts[i + 1], distance)

    def distance_at_station(
        self,
        station: Station,
        mode: ExtrapolationMode = ExtrapolationMode.NONE,
    ) -> float:
        pts = self.active_set.points
        if not pts:
            raise CalibrationError("No calibration points available")
        s_vals = [getattr(getattr(p, "_station", None), "_value", 0.0) for p in pts]
        s0 = s_vals[0]
        sn = s_vals[-1]
        sv = station._value
        if sv < min(s0, sn) or sv > max(s0, sn):
            return self._extrapolate_distance(station, pts, s_vals, s0, sn, mode)
        i = bisect.bisect_right(s_vals, sv) - 1
        if i < 0:
            i = 0
        if i >= len(pts) - 1:
            i = len(pts) - 2
        return self._interpolate_distance(pts[i], pts[i + 1], sv)

    def interpolate(self, distance: float) -> Station:
        return self.station_at_distance(distance, ExtrapolationMode.NONE)

    def extrapolate(self, distance: float) -> Station:
        return self.station_at_distance(distance, ExtrapolationMode.LINEAR)

    def validate(self) -> list[CalibrationIssue]:
        issues: list[CalibrationIssue] = []
        for cs in self._sets.values():
            issues.extend(cs.validate())  # type: ignore[arg-type]
        active = self.active_set
        pts = active.points
        if len(pts) >= 2:
            for i in range(1, len(pts)):
                prev_s = getattr(getattr(pts[i - 1], "_station", None), "_value", 0.0)
                curr_s = getattr(getattr(pts[i], "_station", None), "_value", 0.0)
                if curr_s < prev_s:
                    from dinpro.domain.linear_referencing.calibration_issue import (
                        CalibrationIssue,
                        CalibrationSeverity,
                    )
                    issues.append(CalibrationIssue(
                        severity=CalibrationSeverity.WARNING,
                        code="RC003",
                        message=f"Decreasing PK at index {i}: "
                                f"{prev_s} -> {curr_s}",
                        point_index=i,
                    ))
        return issues

    @staticmethod
    def _interpolate_station(
        p1: object, p2: object, distance: float
    ) -> Station:
        from dinpro.domain.linear_referencing.station import Station

        d1 = getattr(p1, "_distance", 0.0)
        d2 = getattr(p2, "_distance", 0.0)
        s1 = getattr(getattr(p1, "_station", None), "_value", 0.0)
        s2 = getattr(getattr(p2, "_station", None), "_value", 0.0)
        if abs(d2 - d1) < 1e-12:
            return Station(s1)
        ratio = (distance - d1) / (d2 - d1)
        s_val = s1 + ratio * (s2 - s1)
        return Station(s_val)

    @staticmethod
    def _interpolate_distance(p1: object, p2: object, station_value: float) -> float:
        d1 = getattr(p1, "_distance", 0.0)
        d2 = getattr(p2, "_distance", 0.0)
        s1 = getattr(getattr(p1, "_station", None), "_value", 0.0)
        s2 = getattr(getattr(p2, "_station", None), "_value", 0.0)
        if abs(s2 - s1) < 1e-12:
            return d1
        ratio = (station_value - s1) / (s2 - s1)
        return d1 + ratio * (d2 - d1)

    @staticmethod
    def _extrapolate_station(
        distance: float,
        pts: tuple[object, ...],
        d0: float,
        dn: float,
        mode: ExtrapolationMode,
    ) -> Station:
        from dinpro.domain.linear_referencing.station import Station

        if mode == ExtrapolationMode.NONE:
            raise CalibrationError(
                f"Distance {distance} outside calibrated range [{d0}, {dn}]"
            )
        if mode == ExtrapolationMode.CONSTANT:
            if distance < d0:
                return Station(getattr(getattr(pts[0], "_station", None), "_value", 0.0))
            return Station(getattr(getattr(pts[-1], "_station", None), "_value", 0.0))
        if distance < d0:
            return RouteCalibration._interpolate_station(pts[0], pts[1], distance)
        return RouteCalibration._interpolate_station(pts[-2], pts[-1], distance)

    @staticmethod
    def _extrapolate_distance(
        station: Station,
        pts: tuple[object, ...],
        s_vals: list[float],
        s0: float,
        sn: float,
        mode: ExtrapolationMode,
    ) -> float:
        sv = station._value
        if mode == ExtrapolationMode.NONE:
            raise CalibrationError(
                f"Station {sv} outside calibrated range [{s0}, {sn}]"
            )
        if mode == ExtrapolationMode.CONSTANT:
            if sv < s0:
                return getattr(pts[0], "_distance", 0.0)
            return getattr(pts[-1], "_distance", 0.0)
        if sv < min(s0, sn):
            return RouteCalibration._interpolate_distance(pts[0], pts[1], sv)
        return RouteCalibration._interpolate_distance(pts[-2], pts[-1], sv)
