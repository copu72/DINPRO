from __future__ import annotations

from typing import Any

from dinpro.domain.crs.crs import CRS
from dinpro.domain.geometry.circle import Circle
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.topology.validator import (
    IssueSeverity,
    TopologyValidator,
    ValidationIssue,
    ValidationResult,
)


class GeometryValidator:
    def __init__(self, tolerance: float = 1e-10) -> None:
        self._topology = TopologyValidator(tolerance=tolerance)
        self._tolerance = tolerance

    def validate(self, geometry: Point | Line | Polyline | Polygon | Circle,
                 crs: CRS | None = None, context: dict[str, Any] | None = None) -> ValidationResult:
        result = self._topology.validate(geometry)
        result = result.merge(self._validate_crs(geometry, crs))
        result = result.merge(self._validate_context(geometry, context))
        return result

    def validate_axis(self, axis: Any) -> ValidationResult:
        from dinpro.domain.axis import Axis
        if not isinstance(axis, Axis):
            return ValidationResult(valid=False, issues=[
                ValidationIssue(code="NOT_AXIS", message="Object is not an Axis instance",
                                severity=IssueSeverity.ERROR),
            ])
        result = self._topology.validate(axis.polyline)
        if axis.crs:
            result = result.merge(self._validate_crs(axis.polyline, axis.crs))
        return result

    def _validate_crs(self, geometry: Point | Line | Polyline | Polygon | Circle,
                      crs: CRS | None) -> ValidationResult:
        if crs is None:
            return ValidationResult(valid=True)
        issues: list[ValidationIssue] = []
        if isinstance(geometry, Point):
            issues.extend(self._check_crs_bounds(geometry, crs))
        return ValidationResult(valid=len(issues) == 0, issues=issues)

    def _validate_context(self, geometry: Point | Line | Polyline | Polygon | Circle,
                          context: dict[str, Any] | None) -> ValidationResult:
        if context is None:
            return ValidationResult(valid=True)
        issues: list[ValidationIssue] = []
        if "max_length" in context and isinstance(geometry, (Line, Polyline)):
            ln = geometry.length()
            if ln > context["max_length"]:
                issues.append(ValidationIssue(
                    code="MAX_LENGTH_EXCEEDED",
                    message=f"Length {ln:.2f} exceeds max {context['max_length']:.2f}",
                    severity=IssueSeverity.ERROR,
                ))
        if "max_vertices" in context and isinstance(geometry, Polyline):
            if geometry.vertex_count() > context["max_vertices"]:
                issues.append(ValidationIssue(
                    code="MAX_VERTICES_EXCEEDED",
                    message=(
                        f"Vertices {geometry.vertex_count()}"
                        f" exceeds max {context['max_vertices']}"
                    ),
                    severity=IssueSeverity.WARNING,
                ))
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        return ValidationResult(valid=len(errors) == 0, issues=issues)

    @staticmethod
    def _check_crs_bounds(point: Point, crs: CRS) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if crs.is_utm():
            if point.x < 100000 or point.x > 1000000:
                issues.append(ValidationIssue(
                    code="CRS_OUT_OF_BOUNDS",
                    message=f"Easting {point.x:.2f} outside typical UTM range [100000, 1000000]",
                    severity=IssueSeverity.WARNING,
                ))
            if point.y < 0 or point.y > 10000000:
                issues.append(ValidationIssue(
                    code="CRS_OUT_OF_BOUNDS",
                    message=f"Northing {point.y:.2f} outside typical UTM range [0, 10000000]",
                    severity=IssueSeverity.WARNING,
                ))
        if crs.is_geographic():
            if point.x < -90 or point.x > 90:
                issues.append(ValidationIssue(
                    code="CRS_OUT_OF_BOUNDS",
                    message=f"Latitude {point.x:.2f} outside [-90, 90]",
                    severity=IssueSeverity.ERROR,
                ))
            if point.y < -180 or point.y > 180:
                issues.append(ValidationIssue(
                    code="CRS_OUT_OF_BOUNDS",
                    message=f"Longitude {point.y:.2f} outside [-180, 180]",
                    severity=IssueSeverity.ERROR,
                ))
        return issues
