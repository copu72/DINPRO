import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.vector import Vector


class TestVector:
    def test_creation(self):
        v = Vector(1, 2, 3)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_from_points(self):
        v = Vector.from_points(Point(0, 0), Point(3, 4))
        assert v == Vector(3, 4, 0)

    def test_length(self):
        assert math.isclose(Vector(3, 4, 0).length(), 5.0)

    def test_length_3d(self):
        assert math.isclose(Vector(1, 1, 1).length(), math.sqrt(3))

    def test_length_2d(self):
        assert math.isclose(Vector(3, 4, 10).length_2d(), 5.0)

    def test_normalize(self):
        n = Vector(3, 4).normalize()
        assert math.isclose(n.length(), 1.0)
        assert math.isclose(n.x, 0.6)

    def test_normalize_zero(self):
        n = Vector(0, 0).normalize()
        assert n == Vector(0, 0, 0)

    def test_dot(self):
        v1 = Vector(1, 0, 0)
        v2 = Vector(0, 1, 0)
        assert math.isclose(v1.dot(v2), 0.0)

    def test_cross(self):
        v1 = Vector(1, 0, 0)
        v2 = Vector(0, 1, 0)
        c = v1.cross(v2)
        assert c == Vector(0, 0, 1)

    def test_angle_to(self):
        v1 = Vector(1, 0)
        v2 = Vector(0, 1)
        assert math.isclose(v1.angle_to(v2), math.pi / 2)

    def test_angle_to_zero(self):
        v = Vector(0, 0)
        assert v.angle_to(Vector(1, 0)) == 0.0

    def test_angle_2d(self):
        assert math.isclose(Vector(0, 1).angle_2d(), math.pi / 2)

    def test_scale(self):
        s = Vector(1, 2, 3).scale(2)
        assert s == Vector(2, 4, 6)

    def test_add(self):
        s = Vector(1, 0).add(Vector(0, 1))
        assert s == Vector(1, 1)

    def test_subtract(self):
        s = Vector(3, 3).subtract(Vector(1, 1))
        assert s == Vector(2, 2)

    def test_to_tuple(self):
        assert Vector(1, 2, 3).to_tuple() == (1.0, 2.0, 3.0)

    def test_equality(self):
        assert Vector(1, 2) == Vector(1, 2)
        assert Vector(1, 2) != Vector(1, 3)

    def test_hash(self):
        s = {Vector(1, 2), Vector(1, 2)}
        assert len(s) == 1
