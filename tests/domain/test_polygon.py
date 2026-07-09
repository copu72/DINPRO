import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon


class TestPolygon:
    def test_creation(self):
        poly = Polygon.from_xy([(0, 0), (1, 0), (0, 1)])
        assert poly.vertices is not None

    def test_min_vertices(self):
        with pytest.raises(ValueError):
            Polygon.from_xy([(0, 0), (1, 0)])

    def test_area_triangle(self):
        poly = Polygon.from_xy([(0, 0), (1, 0), (0, 1)])
        assert math.isclose(poly.area(), 0.5)

    def test_area_square(self):
        poly = Polygon.from_xy([(0, 0), (1, 0), (1, 1), (0, 1)])
        assert math.isclose(poly.area(), 1.0)

    def test_centroid(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (0, 2)])
        c = poly.centroid()
        assert math.isclose(c.x, 2/3, abs_tol=1e-10)
        assert math.isclose(c.y, 2/3, abs_tol=1e-10)

    def test_contains_point_inside(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (2, 2), (0, 2)])
        assert poly.contains_point(Point(1, 1))

    def test_contains_point_outside(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (2, 2), (0, 2)])
        assert not poly.contains_point(Point(5, 5))

    def test_perimeter(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (2, 2)])
        assert math.isclose(poly.perimeter(), 4.0 + 2.0 * math.sqrt(2))

    def test_to_coords(self):
        poly = Polygon.from_xy([(0, 0), (1, 0), (0, 1)])
        c = poly.to_coords()
        assert len(c) == 3

    def test_repr(self):
        poly = Polygon.from_xy([(0, 0), (1, 0), (0, 1)])
        r = repr(poly)
        assert "Polygon" in r
