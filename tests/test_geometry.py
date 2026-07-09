import math

import pytest

from dinpro.core.errors import GeometryError
from dinpro.core.geometry import Geometry


class TestGeometry:
    def test_distance(self):
        d = Geometry.distance((0, 0), (3, 4))
        assert d == 5.0

    def test_distance_zero(self):
        d = Geometry.distance((1, 1), (1, 1))
        assert d == 0.0

    def test_angle(self):
        a = Geometry.angle((0, 0), (1, 0))
        assert a == 0.0
        a = Geometry.angle((0, 0), (0, 1))
        assert pytest.approx(a) == math.pi / 2

    def test_azimuth(self):
        a = Geometry.azimuth((0, 0), (1, 0))
        assert a == 0.0
        a = Geometry.azimuth((0, 0), (0, 1))
        assert a == 90.0
        a = Geometry.azimuth((0, 0), (1, 1))
        assert pytest.approx(a) == 45.0

    def test_bounding_box(self):
        points = [(0, 0), (10, 5), (3, 8)]
        bbox = Geometry.bounding_box(points)
        assert bbox == (0, 0, 10, 8)

    def test_bounding_box_empty(self):
        with pytest.raises(GeometryError):
            Geometry.bounding_box([])

    def test_length(self):
        line = [(0, 0), (3, 0), (3, 4)]
        assert Geometry.length(line) == 7.0

    def test_length_single_point(self):
        assert Geometry.length([(0, 0)]) == 0.0

    def test_area_triangle(self):
        triangle = [(0, 0), (4, 0), (0, 3)]
        assert Geometry.area(triangle) == 6.0

    def test_area_square(self):
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        assert Geometry.area(square) == 4.0

    def test_area_less_than_3_points(self):
        assert Geometry.area([(0, 0), (1, 0)]) == 0.0

    def test_interpolate(self):
        line = [(0, 0), (10, 0)]
        point = Geometry.interpolate(line, 0.5)
        assert point == (5.0, 0.0)
        point = Geometry.interpolate(line, 0.0)
        assert point == (0.0, 0.0)
        point = Geometry.interpolate(line, 1.0)
        assert point == (10.0, 0.0)

    def test_interpolate_insufficient_points(self):
        with pytest.raises(GeometryError):
            Geometry.interpolate([(0, 0)], 0.5)

    def test_closest_point_on_line(self):
        result = Geometry.closest_point_on_line((0, 5), (0, 0), (10, 0))
        assert result[:2] == (0.0, 0.0)
        assert pytest.approx(result[2]) == 5.0

        result = Geometry.closest_point_on_line((5, 5), (0, 0), (10, 0))
        assert result[:2] == (5.0, 0.0)
        assert result[2] == 5.0
