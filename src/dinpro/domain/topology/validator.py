from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from dinpro.domain.geometry.circle import Circle
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.polyline import Polyline


class IssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: IssueSeverity
    location: str | None = None


@dataclass
class ValidationResult:
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    def merge(self, other: ValidationResult) -> ValidationResult:
        return ValidationResult(
            valid=self.valid and other.valid,
            issues=self.issues + other.issues,
        )


class TopologyValidator:
    def __init__(self, tolerance: float = 1e-10) -> None:
        self._tolerance = tolerance

    def validate(self, geometry: Point | Line | Polyline | Polygon | Circle) -> ValidationResult:
        if isinstance(geometry, Point):
            return self._validate_point(geometry)
        if isinstance(geometry, Line):
            return self._validate_line(geometry)
        if isinstance(geometry, Polyline):
            return self._validate_polyline(geometry)
        if isinstance(geometry, Polygon):
            return self._validate_polygon(geometry)
        if isinstance(geometry, Circle):
            return self._validate_circle(geometry)
        return ValidationResult(valid=True)

    def validate_all(
        self, geometries: Sequence[Point | Line | Polyline | Polygon | Circle]
    ) -> ValidationResult:
        result = ValidationResult(valid=True)
        for geom in geometries:
            result = result.merge(self.validate(geom))
        return result

    def _validate_point(self, point: Point) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if not math.isfinite(point.x) or not math.isfinite(point.y) or not math.isfinite(point.z):
            issues.append(ValidationIssue(
                code="INF_COORDS", message="Point has infinite or NaN coordinates",
                severity=IssueSeverity.ERROR, location=str(point),
            ))
        return ValidationResult(valid=len(issues) == 0, issues=issues)

    def _validate_line(self, line: Line) -> ValidationResult:
        issues: list[ValidationIssue] = []
        issues.extend(self._validate_point(line.start).issues)
        issues.extend(self._validate_point(line.end).issues)
        if line.start.distance_to(line.end) < self._tolerance:
            issues.append(ValidationIssue(
                code="ZERO_LENGTH", message="Line has zero length",
                severity=IssueSeverity.ERROR, location=str(line),
            ))
        errs = [i for i in issues if i.severity == IssueSeverity.ERROR]
        return ValidationResult(valid=len(errs) == 0, issues=issues)

    def _validate_polyline(self, polyline: Polyline) -> ValidationResult:
        issues: list[ValidationIssue] = []
        verts = polyline.vertices
        if polyline.vertex_count() < 2:
            issues.append(ValidationIssue(
                code="NOT_ENOUGH_VERTICES",
                message=f"Polyline has only {polyline.vertex_count()} vertices, minimum 2",
                severity=IssueSeverity.ERROR,
            ))
            return ValidationResult(valid=False, issues=issues)

        for i, v in enumerate(verts):
            issues.extend(self._validate_point(v).issues)

        for i in range(len(verts) - 1):
            if verts[i].distance_to(verts[i + 1]) < self._tolerance:
                issues.append(ValidationIssue(
                    code="ZERO_LENGTH_SEGMENT",
                    message=f"Zero-length segment between vertices {i} and {i+1}",
                    severity=IssueSeverity.ERROR,
                ))

        seen: set[tuple[float, float, float]] = set()
        for i, v in enumerate(verts):
            key = (round(v.x, 10), round(v.y, 10), round(v.z, 10))
            if key in seen:
                issues.append(ValidationIssue(
                    code="DUPLICATE_VERTEX",
                    message=f"Duplicate vertex at index {i}",
                    severity=IssueSeverity.WARNING,
                ))
            seen.add(key)

        if self._has_self_intersections(polyline):
            issues.append(ValidationIssue(
                code="SELF_INTERSECTION",
                message="Polyline has self-intersections",
                severity=IssueSeverity.ERROR,
            ))

        return ValidationResult(
            valid=len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0,
            issues=issues,
        )

    def _validate_polygon(self, polygon: Polygon) -> ValidationResult:
        issues: list[ValidationIssue] = []
        result = self._validate_polyline(polygon.outer)
        issues.extend(result.issues)
        if polygon.outer.vertex_count() < 3:
            issues.append(ValidationIssue(
                code="NOT_ENOUGH_VERTICES",
                message="Polygon outer ring must have at least 3 vertices",
                severity=IssueSeverity.ERROR,
            ))
        return ValidationResult(
            valid=len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0,
            issues=issues,
        )

    def _validate_circle(self, circle: Circle) -> ValidationResult:
        issues: list[ValidationIssue] = []
        issues.extend(self._validate_point(circle.center).issues)
        if circle.radius < 0:
            issues.append(ValidationIssue(
                code="NEGATIVE_RADIUS", message="Circle has negative radius",
                severity=IssueSeverity.ERROR, location=str(circle),
            ))
        if circle.radius < self._tolerance:
            issues.append(ValidationIssue(
                code="ZERO_RADIUS", message="Circle has zero radius",
                severity=IssueSeverity.WARNING, location=str(circle),
            ))
        return ValidationResult(
            valid=len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0,
            issues=issues,
        )

    def _has_self_intersections(self, polyline: Polyline) -> bool:
        verts = polyline.vertices
        n = len(verts)
        for i in range(n - 1):
            seg1 = Line(verts[i], verts[i + 1])
            for j in range(i + 2, n - 1):
                if i == 0 and j == n - 2 and polyline.closed:
                    continue
                seg2 = Line(verts[j], verts[j + 1])
                if seg1.intersection_2d(seg2) is not None:
                    return True
        if polyline.closed and n > 3:
            seg1 = Line(verts[-1], verts[0])
            for j in range(1, n - 2):
                seg2 = Line(verts[j], verts[j + 1])
                if seg1.intersection_2d(seg2) is not None:
                    return True
        return False
