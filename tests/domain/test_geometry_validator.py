import pytest
from dinpro.domain.geometry_validator import GeometryValidator
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.crs import CRSRegistry
from dinpro.domain.axis import Axis


class TestGeometryValidator:
    @pytest.fixture
    def validator(self):
        return GeometryValidator()

    def test_valid_geometry(self, validator):
        result = validator.validate(Point(1, 2))
        assert result.valid

    def test_invalid_geometry(self, validator):
        result = validator.validate(Line(Point(0, 0), Point(0, 0)))
        assert not result.valid

    def test_with_crs(self, validator):
        crs = CRSRegistry.get("WGS84")
        result = validator.validate(Point(40.0, -3.0), crs)
        assert result.valid

    def test_with_crs_out_of_bounds(self, validator):
        crs = CRSRegistry.get("WGS84")
        result = validator.validate(Point(100.0, 200.0), crs)
        assert not result.valid

    def test_with_utm_crs(self, validator):
        crs = CRSRegistry.get("ETRS89/UTM30N")
        result = validator.validate(Point(500000, 4500000), crs)
        assert result.valid

    def test_with_context_max_length(self, validator):
        polyline = Polyline.from_xy([(0, 0), (100, 0)])
        result = validator.validate(polyline, context={"max_length": 50})
        assert not result.valid

    def test_with_context_max_vertices(self, validator):
        polyline = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        result = validator.validate(polyline, context={"max_vertices": 2})
        assert result.valid

    def test_validate_axis(self, validator):
        axis = Axis.from_xy([(0, 0), (10, 0)])
        result = validator.validate_axis(axis)
        assert result.valid

    def test_validate_axis_not_axis(self, validator):
        result = validator.validate_axis("not_an_axis")
        assert not result.valid
