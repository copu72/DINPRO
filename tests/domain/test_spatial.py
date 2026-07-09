import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.line import Line
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.circle import Circle
from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.spatial import SpatialOperations


class TestSpatial:
    def test_distance_point_point(self):
        d = SpatialOperations.distance(Point(0, 0), Point(3, 4))
        assert math.isclose(d, 5.0)

    def test_distance_point_line(self):
        line = Line(Point(0, 0), Point(10, 0))
        d = SpatialOperations.distance(Point(5, 3), line)
        assert math.isclose(d, 3.0)

    def test_distance_line_point(self):
        line = Line(Point(0, 0), Point(10, 0))
        d = SpatialOperations.distance(line, Point(5, 3))
        assert math.isclose(d, 3.0)

    def test_intersects_bbox(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(5, 5, 15, 15)
        assert SpatialOperations.intersects(bb1, bb2)

    def test_not_intersects_bbox(self):
        bb1 = BoundingBox(0, 0, 10, 10)
        bb2 = BoundingBox(20, 20, 30, 30)
        assert not SpatialOperations.intersects(bb1, bb2)

    def test_polygon_contains_point(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (2, 2), (0, 2)])
        assert SpatialOperations.contains(poly, Point(1, 1))

    def test_circle_contains_point(self):
        c = Circle(Point(0, 0), 5)
        assert SpatialOperations.contains(c, Point(3, 0))

    def test_within(self):
        poly = Polygon.from_xy([(0, 0), (2, 0), (2, 2), (0, 2)])
        assert SpatialOperations.within(Point(1, 1), poly)

    def test_nearest(self):
        polyline = Polyline.from_xy([(0, 0), (10, 0)])
        np, dist, idx = SpatialOperations.nearest(
            Point(5, 3), [Point(0, 0), polyline]
        )
        assert math.isclose(dist, 3.0)

    def test_buffer(self):
        poly = Polyline.from_xy([(0, 0), (10, 0)])
        buf = SpatialOperations.buffer(poly, 2.0)
        assert buf.vertex_count() == 2

    def test_offset_left(self):
        poly = Polyline.from_xy([(0, 0), (10, 0)])
        off = SpatialOperations.offset(poly, 2.0, side="left")
        assert off.vertex(0).y > 0

    def test_offset_right(self):
        poly = Polyline.from_xy([(0, 0), (10, 0)])
        off = SpatialOperations.offset(poly, 2.0, side="right")
        assert off.vertex(0).y < 0

    def test_clip(self):
        poly = Polyline.from_xy([(0, 0), (20, 0)])
        bbox = BoundingBox(5, -1, 15, 1)
        clipped = SpatialOperations.clip(poly, bbox)
        assert clipped.vertex_count() >= 2

    def test_split(self):
        poly = Polyline.from_xy([(0, 0), (10, 0)])
        left, right = SpatialOperations.split(poly, Point(5, 0))
        assert math.isclose(left.length(), 5.0)
        assert math.isclose(right.length(), 5.0)

    def test_merge(self):
        a = Polyline.from_xy([(0, 0), (5, 0)])
        b = Polyline.from_xy([(5, 0), (10, 0)])
        merged = SpatialOperations.merge(a, b)
        assert math.isclose(merged.length(), 10.0)

    def test_touches(self):
        poly1 = Polyline.from_xy([(0, 0), (5, 0)])
        poly2 = Polyline.from_xy([(5, 0), (10, 0)])
        assert SpatialOperations.touches(poly1, poly2)
