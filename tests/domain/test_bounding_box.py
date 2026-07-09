import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.bounding_box import BoundingBox


class TestBoundingBox:
    def test_creation(self):
        bb = BoundingBox(0, 0, 10, 10)
        assert bb.xmin == 0
        assert bb.xmax == 10
        assert bb.ymin == 0
        assert bb.ymax == 10

    def test_invalid(self):
        with pytest.raises(ValueError):
            BoundingBox(10, 0, 0, 10)

    def test_from_points(self):
        bb = BoundingBox.from_points([Point(1, 2), Point(5, 7)])
        assert bb.xmin == 1
        assert bb.xmax == 5
        assert bb.ymin == 2
        assert bb.ymax == 7

    def test_from_points_empty(self):
        with pytest.raises(ValueError):
            BoundingBox.from_points([])

    def test_width(self):
        bb = BoundingBox(0, 0, 10, 5)
        assert bb.width() == 10

    def test_height(self):
        bb = BoundingBox(0, 0, 10, 5)
        assert bb.height() == 5

    def test_center(self):
        bb = BoundingBox(0, 0, 10, 10)
        c = bb.center()
        assert c == Point(5, 5)

    def test_contains(self):
        outer = BoundingBox(0, 0, 10, 10)
        inner = BoundingBox(1, 1, 9, 9)
        assert outer.contains(inner)

    def test_not_contains(self):
        outer = BoundingBox(0, 0, 10, 10)
        other = BoundingBox(5, 5, 15, 15)
        assert not outer.contains(other)

    def test_intersects(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(5, 5, 15, 15)
        assert bb1.intersects(bb2)

    def test_not_intersects(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(20, 20, 30, 30)
        assert not bb1.intersects(bb2)

    def test_expand(self):
        bb = BoundingBox(0, 0, 10, 10)
        e = bb.expand(5)
        assert e == BoundingBox(-5, -5, 15, 15)

    def test_union(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(5, 5, 15, 15)
        u = bb1.union(bb2)
        assert u == BoundingBox(0, 0, 15, 15)

    def test_intersection(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(5, 5, 15, 15)
        i = bb1.intersection(bb2)
        assert i == BoundingBox(5, 5, 10, 10)

    def test_intersection_none(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(20, 20, 30, 30)
        assert bb1.intersection(bb2) is None

    def test_area(self):
        bb = BoundingBox(0, 0, 10, 5)
        assert bb.area() == 50

    def test_to_tuple(self):
        bb = BoundingBox(0, 0, 10, 10)
        assert bb.to_tuple() == (0.0, 0.0, 10.0, 10.0)

    def test_repr(self):
        r = repr(BoundingBox(0, 0, 10, 10))
        assert "BoundingBox" in r
