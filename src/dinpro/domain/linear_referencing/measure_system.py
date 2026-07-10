from __future__ import annotations

import bisect
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis


@dataclass
class CalibrationPoint:
    pk: float
    distance: float


@dataclass
class MeasureDiscontinuity:
    start_pk: float
    end_pk: float
    gap_before: float


class MeasureSystem:
    def __init__(
        self,
        axis: Axis | None = None,
        calibrations: list[CalibrationPoint] | None = None,
    ) -> None:
        self._axis = axis
        self._calibrations: list[CalibrationPoint] = []
        self._discontinuities: list[MeasureDiscontinuity] = []
        self._direction = 1
        if calibrations:
            for c in sorted(calibrations, key=lambda x: x.distance):
                self._calibrations.append(c)

    def pk_at_distance(self, distance: float) -> float:
        if not self._calibrations:
            return distance
        i = bisect.bisect_right([c.distance for c in self._calibrations], distance)
        if i == 0:
            return distance
        if i >= len(self._calibrations):
            last = self._calibrations[-1]
            return last.pk + (distance - last.distance)
        c0 = self._calibrations[i - 1]
        c1 = self._calibrations[i]
        if c1.distance - c0.distance == 0:
            return c1.pk
        ratio = (distance - c0.distance) / (c1.distance - c0.distance)
        return c0.pk + ratio * (c1.pk - c0.pk)

    def distance_at_pk(self, pk: float) -> float:
        if not self._calibrations:
            return pk
        i = bisect.bisect_right([c.pk for c in self._calibrations], pk)
        if i == 0:
            return pk
        if i >= len(self._calibrations):
            last = self._calibrations[-1]
            return last.distance + (pk - last.pk)
        c0 = self._calibrations[i - 1]
        c1 = self._calibrations[i]
        if c1.pk - c0.pk == 0:
            return c1.distance
        ratio = (pk - c0.pk) / (c1.pk - c0.pk)
        return c0.distance + ratio * (c1.distance - c0.distance)

    def calibrate(self, points: list[CalibrationPoint]) -> None:
        for p in points:
            if p.pk < 0:
                raise ValueError(f"Calibration PK cannot be negative: {p.pk}")
            existing = [c for c in self._calibrations if c.pk == p.pk]
            if existing:
                existing[0].distance = p.distance
            else:
                self._calibrations.append(p)
        self._calibrations.sort(key=lambda x: x.distance)

    def add_discontinuity(self, pk: float, gap: float) -> None:
        self._discontinuities.append(MeasureDiscontinuity(pk, pk, gap))

    def total_measure(self) -> float:
        if self._axis is None:
            if self._calibrations:
                return max(c.pk for c in self._calibrations)
            return 0.0
        raw_length = self._axis.length
        if not self._calibrations:
            return raw_length
        return self.pk_at_distance(raw_length)

    def validate(self) -> list[str]:
        warnings: list[str] = []
        for c in self._calibrations:
            if c.pk < 0:
                warnings.append(f"Negative calibration PK: {c.pk}")
        if len(self._calibrations) >= 2:
            total_geo = self._calibrations[-1].distance - self._calibrations[0].distance
            total_pk = self._calibrations[-1].pk - self._calibrations[0].pk
            if total_geo > 0:
                deviation = abs(total_pk - total_geo) / total_geo
                if deviation > 0.01:
                    warnings.append(
                        f"Calibration deviation {deviation:.2%} exceeds 1%"
                    )
        return warnings

    def clear(self) -> None:
        self._calibrations.clear()
        self._discontinuities.clear()

    @property
    def calibrations(self) -> list[CalibrationPoint]:
        return list(self._calibrations)

    @property
    def discontinuities(self) -> list[MeasureDiscontinuity]:
        return list(self._discontinuities)

    @property
    def is_calibrated(self) -> bool:
        return len(self._calibrations) > 0
