import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.circle import Circle


class TestCircle:
    def test_creation(self):
        c = Circle(Point(0, 0), 5)
        assert c.center == Point(0, 0)
        assert c.radius == 5.0

    def test_from_coords(self):
        c = Circle.from_coords(1, 2, 3)
        assert c.center == Point(1, 2)

    def test_negative_radius(self):
        with pytest.raises(ValueError):
            Circle(Point(0, 0), -1)

    def test_area(self):
        c = Circle(Point(0, 0), 1)
        assert math.isclose(c.area(), math.pi)

    def test_circumference(self):
        c = Circle(Point(0, 0), 1)
        assert math.isclose(c.circumference(), 2 * math.pi)

    def test_diameter(self):
        c = Circle(Point(0, 0), 5)
        assert c.diameter() == 10.0

    def test_bounding_box(self):
        c = Circle(Point(0, 0), 5)
        bb = c.bounding_box()
        assert bb.xmin == -5
        assert bb.xmax == 5
        assert bb.ymin == -5
        assert bb.ymax == 5

    def test_contains_point_inside(self):
        c = Circle(Point(0, 0), 5)
        assert c.contains_point(Point(3, 0))

    def test_contains_point_outside(self):
        c = Circle(Point(0, 0), 5)
        assert not c.contains_point(Point(6, 0))

    def test_distance_to_point(self):
        c = Circle(Point(0, 0), 5)
        d = c.distance_to_point(Point(8, 0))
        assert math.isclose(d, 3.0)

    def test_distance_to_point_inside(self):
        c = Circle(Point(0, 0), 5)
        d = c.distance_to_point(Point(2, 0))
        assert math.isclose(d, 0.0)

    def test_point_at_angle(self):
        c = Circle(Point(0, 0), 5)
        p = c.point_at_angle(0)
        assert p == Point(5, 0)

    def test_to_tuple(self):
        c = Circle(Point(1, 2), 3)
        t = c.to_tuple()
        assert t == ((1.0, 2.0, 0.0), 3.0)

    def test_repr(self):
        r = repr(Circle(Point(0, 0), 5))
        assert "Circle" in r
