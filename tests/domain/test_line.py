import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.vector import Vector


class TestLine:
    def test_creation(self):
        l = Line(Point(0, 0), Point(3, 4))
        assert l.start == Point(0, 0)
        assert l.end == Point(3, 4)

    def test_from_coords(self):
        l = Line.from_coords(0, 0, 3, 4)
        assert l.length() == 5.0

    def test_length(self):
        l = Line(Point(0, 0), Point(3, 4))
        assert math.isclose(l.length(), 5.0)

    def test_length_2d(self):
        l = Line(Point(0, 0, 10), Point(3, 4, 20))
        assert math.isclose(l.length_2d(), 5.0)

    def test_as_vector(self):
        l = Line(Point(0, 0), Point(3, 4))
        v = l.as_vector()
        assert v == Vector(3, 4, 0)

    def test_direction(self):
        l = Line(Point(0, 0), Point(3, 4))
        d = l.direction()
        assert math.isclose(d.length(), 1.0)

    def test_midpoint(self):
        l = Line(Point(0, 0), Point(2, 4))
        m = l.midpoint()
        assert m == Point(1, 2)

    def test_point_at(self):
        l = Line(Point(0, 0), Point(10, 0))
        p = l.point_at(0.5)
        assert p == Point(5, 0)

    def test_point_at_distance(self):
        l = Line(Point(0, 0), Point(10, 0))
        p = l.point_at_distance(3)
        assert p == Point(3, 0)

    def test_distance_to_point(self):
        l = Line(Point(0, 0), Point(10, 0))
        d = l.distance_to_point(Point(5, 3))
        assert math.isclose(d, 3.0)

    def test_nearest_point_on(self):
        l = Line(Point(0, 0), Point(10, 0))
        np = l.nearest_point_on(Point(5, 3))
        assert np == Point(5, 0)

    def test_nearest_point_beyond(self):
        l = Line(Point(0, 0), Point(10, 0))
        np = l.nearest_point_on(Point(15, 3))
        assert np == Point(10, 0)

    def test_azimuth(self):
        l = Line(Point(0, 0), Point(1, 1))
        assert math.isclose(l.azimuth(), math.pi / 4)

    def test_is_parallel(self):
        l1 = Line(Point(0, 0), Point(1, 0))
        l2 = Line(Point(0, 1), Point(1, 1))
        assert l1.is_parallel_to(l2)

    def test_not_parallel(self):
        l1 = Line(Point(0, 0), Point(1, 0))
        l2 = Line(Point(0, 0), Point(1, 1))
        assert not l1.is_parallel_to(l2)

    def test_intersection_2d(self):
        l1 = Line(Point(0, 0), Point(2, 0))
        l2 = Line(Point(1, -1), Point(1, 1))
        p = l1.intersection_2d(l2)
        assert p is not None
        assert p == Point(1, 0)

    def test_no_intersection(self):
        l1 = Line(Point(0, 0), Point(1, 0))
        l2 = Line(Point(2, 0), Point(3, 0))
        p = l1.intersection_2d(l2)
        assert p is None

    def test_intersection_parallel(self):
        l1 = Line(Point(0, 0), Point(1, 0))
        l2 = Line(Point(0, 1), Point(1, 1))
        p = l1.intersection_2d(l2)
        assert p is None

    def test_to_tuple(self):
        l = Line(Point(1, 2), Point(3, 4))
        t = l.to_tuple()
        assert t == ((1.0, 2.0, 0.0), (3.0, 4.0, 0.0))

    def test_repr(self):
        r = repr(Line(Point(0, 0), Point(1, 1)))
        assert "Line" in r
