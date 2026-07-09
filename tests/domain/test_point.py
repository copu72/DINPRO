import math
import pytest
from dinpro.domain.geometry.point import Point


class TestPoint:
    def test_creation_2d(self):
        p = Point(1.0, 2.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 0.0

    def test_creation_3d(self):
        p = Point(1.0, 2.0, 3.0)
        assert p.z == 3.0

    def test_distance_to(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert math.isclose(p1.distance_to(p2), 5.0)

    def test_distance_to_3d(self):
        p1 = Point(0, 0, 0)
        p2 = Point(1, 1, 1)
        assert math.isclose(p1.distance_to(p2), math.sqrt(3))

    def test_distance_2d(self):
        p1 = Point(0, 0, 10)
        p2 = Point(3, 4, 20)
        assert math.isclose(p1.distance_2d(p2), 5.0)

    def test_midpoint(self):
        p1 = Point(0, 0)
        p2 = Point(2, 4)
        m = p1.midpoint(p2)
        assert m == Point(1, 2)

    def test_translate(self):
        p = Point(1, 2, 3)
        t = p.translate(10, 20, 30)
        assert t == Point(11, 22, 33)

    def test_rotate_2d(self):
        p = Point(1, 0)
        r = p.rotate_2d(math.pi / 2)
        assert math.isclose(r.x, 0, abs_tol=1e-10)
        assert math.isclose(r.y, 1, abs_tol=1e-10)

    def test_rotate_2d_with_center(self):
        p = Point(2, 0)
        center = Point(1, 0)
        r = p.rotate_2d(math.pi / 2, center)
        assert math.isclose(r.x, 1, abs_tol=1e-10)
        assert math.isclose(r.y, 1, abs_tol=1e-10)

    def test_to_tuple(self):
        p = Point(1, 2, 3)
        assert p.to_tuple() == (1.0, 2.0, 3.0)

    def test_to_tuple_2d(self):
        p = Point(1, 2, 3)
        assert p.to_tuple_2d() == (1.0, 2.0)

    def test_equality(self):
        assert Point(1, 2) == Point(1, 2)
        assert Point(1, 2, 3) != Point(1, 2, 4)

    def test_hash(self):
        s = {Point(1, 2), Point(1, 2)}
        assert len(s) == 1

    def test_repr(self):
        r = repr(Point(1.5, 2.5))
        assert "Point" in r

    def test_equality_with_non_point(self):
        assert (Point(1, 2) == "not_a_point") is False
