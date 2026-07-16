from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis


@dataclass(frozen=True)
class CalibrationSet:
    _campaign_id: str
    _axis: object
    _points: tuple[object, ...]
    _created_at: str = ""
    _source: str = "manual"

    def __post_init__(self) -> None:
        from dinpro.domain.linear_referencing.calibration_point import CalibrationPoint

        if not self._created_at:
            object.__setattr__(self, "_created_at", datetime.now(timezone.utc).isoformat())
        if not self._points:
            raise ValueError("CalibrationSet must have at least one point")
        for p in self._points:
            if not isinstance(p, CalibrationPoint):
                raise TypeError(f"Each point must be a CalibrationPoint, got {type(p)}")

    @property
    def campaign_id(self) -> str:
        return self._campaign_id

    @property
    def axis(self) -> Axis:
        return self._axis  # type: ignore[return-value]

    @property
    def points(self) -> tuple[object, ...]:
        return self._points

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def source(self) -> str:
        return self._source

    def validate(self) -> list[object]:
        from dinpro.domain.linear_referencing.calibration_issue import (
            CalibrationIssue,
            CalibrationSeverity,
        )

        issues: list[object] = []
        if len(self._points) < 2:
            issues.append(CalibrationIssue(
                severity=CalibrationSeverity.ERROR,
                code="RC001",
                message="CalibrationSet requires at least 2 points for interpolation",
            ))
            return issues
        for i, p in enumerate(self._points):
            if i == 0:
                continue
            prev = self._points[i - 1]
            p_dist = getattr(p, "_distance", 0.0)
            prev_dist = getattr(prev, "_distance", 0.0)
            if p_dist <= prev_dist:
                issues.append(CalibrationIssue(
                    severity=CalibrationSeverity.ERROR,
                    code="RC002",
                    message=f"Points not strictly increasing at index {i}: "
                            f"{prev_dist} >= {p_dist}",
                    point_index=i,
                ))
        return issues
