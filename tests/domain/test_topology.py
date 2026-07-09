import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.circle import Circle
from dinpro.domain.topology import TopologyValidator
from dinpro.domain.topology.validator import IssueSeverity


class TestTopologyValidator:
    @pytest.fixture
    def validator(self):
        return TopologyValidator()

    def test_valid_point(self, validator):
        result = validator.validate(Point(1, 2))
        assert result.valid

    def test_inf_point(self, validator):
        import math
        result = validator.validate(Point(float("inf"), 0))
        assert not result.valid

    def test_valid_line(self, validator):
        result = validator.validate(Line(Point(0, 0), Point(1, 0)))
        assert result.valid

    def test_zero_length_line(self, validator):
        result = validator.validate(Line(Point(0, 0), Point(0, 0)))
        assert not result.valid

    def test_valid_polyline(self, validator):
        result = validator.validate(Polyline.from_xy([(0, 0), (1, 0), (2, 0)]))
        assert result.valid

    def test_polyline_not_enough_vertices(self, validator):
        result = validator.validate(Polyline.from_xy([(0, 0), (1, 0)]))
        assert result.valid

    def test_zero_length_segment(self, validator):
        result = validator.validate(Polyline.from_xy([(0, 0), (0, 0), (1, 0)]))
        assert not result.valid

    def test_duplicate_vertex(self, validator):
        result = validator.validate(Polyline.from_xy([(0, 0), (1, 0), (0, 0)]))
        warnings = [i for i in result.issues if i.severity == IssueSeverity.WARNING]
        assert any("DUPLICATE" in i.code for i in warnings)

    def test_self_intersection(self, validator):
        result = validator.validate(
            Polyline.from_xy([(0, 0), (2, 2), (0, 2), (2, 0)])
        )
        errors = [i for i in result.issues if i.severity == IssueSeverity.ERROR]
        assert any("SELF_INTERSECTION" in i.code for i in errors)

    def test_valid_polygon(self, validator):
        result = validator.validate(Polygon.from_xy([(0, 0), (1, 0), (0, 1)]))
        assert result.valid

    def test_valid_circle(self, validator):
        result = validator.validate(Circle(Point(0, 0), 5))
        assert result.valid

    def test_negative_radius_circle(self, validator):
        with pytest.raises(ValueError):
            validator.validate(Circle(Point(0, 0), -1))

    def test_validate_all(self, validator):
        result = validator.validate_all([
            Point(1, 2),
            Line(Point(0, 0), Point(1, 0)),
        ])
        assert result.valid

    def test_merge_result(self, validator):
        r1 = validator.validate(Point(1, 2))
        r2 = validator.validate(Line(Point(0, 0), Point(1, 0)))
        merged = r1.merge(r2)
        assert merged.valid
