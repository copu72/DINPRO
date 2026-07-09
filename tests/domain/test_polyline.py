import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline


class TestPolyline:
    def test_creation(self):
        p = Polyline.from_xy([(0, 0), (1, 1), (2, 0)])
        assert p.vertex_count() == 3

    def test_min_vertices(self):
        with pytest.raises(ValueError):
            Polyline.from_xy([(0, 0)])

    def test_vertices(self):
        p = Polyline.from_xy([(0, 0), (1, 1)])
        verts = p.vertices
        assert len(verts) == 2

    def test_segment_count_open(self):
        p = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        assert p.segment_count() == 2

    def test_segment_count_closed(self):
        p = Polyline.from_xy([(0, 0), (1, 0), (2, 0)], closed=True)
        assert p.segment_count() == 3

    def test_segment(self):
        p = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        seg = p.segment(1)
        assert seg.start == Point(1, 0)
        assert seg.end == Point(2, 0)

    def test_segments(self):
        p = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        segs = p.segments()
        assert len(segs) == 2

    def test_length(self):
        p = Polyline.from_xy([(0, 0), (3, 0), (3, 4)])
        assert math.isclose(p.length(), 7.0)

    def test_vertex(self):
        p = Polyline.from_xy([(0, 0), (1, 1)])
        assert p.vertex(1) == Point(1, 1)

    def test_centroid(self):
        p = Polyline.from_xy([(0, 0), (2, 0), (2, 2)])
        c = p.centroid()
        assert c == Point(4/3, 2/3, 0)

    def test_bounding_box(self):
        p = Polyline.from_xy([(0, 0), (3, 4)])
        bb = p.bounding_box()
        assert bb.xmin == 0
        assert bb.xmax == 3
        assert bb.ymin == 0
        assert bb.ymax == 4

    def test_point_at_distance(self):
        p = Polyline.from_xy([(0, 0), (10, 0)])
        pt = p.point_at_distance(3)
        assert pt == Point(3, 0)

    def test_point_at_distance_open_beyond(self):
        p = Polyline.from_xy([(0, 0), (10, 0)])
        pt = p.point_at_distance(20)
        assert pt == Point(10, 0)

    def test_nearest_point_on(self):
        p = Polyline.from_xy([(0, 0), (10, 0)])
        np, seg, dist = p.nearest_point_on(Point(5, 3))
        assert np == Point(5, 0)
        assert dist == 3.0

    def test_reverse(self):
        p = Polyline.from_xy([(0, 0), (1, 1), (2, 0)])
        r = p.reverse()
        assert r.vertex(0) == Point(2, 0)
        assert r.vertex(2) == Point(0, 0)

    def test_append(self):
        p = Polyline.from_xy([(0, 0), (1, 0)])
        p2 = p.append(Point(2, 0))
        assert p2.vertex_count() == 3

    def test_insert(self):
        p = Polyline.from_xy([(0, 0), (2, 0)])
        p2 = p.insert(1, Point(1, 0))
        assert p2.vertex_count() == 3

    def test_remove(self):
        p = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        p2 = p.remove(1)
        assert p2.vertex_count() == 2

    def test_simplify(self):
        p = Polyline.from_xy([(0, 0), (0.5, 0.01), (1, 0)])
        s = p.simplify(0.1)
        assert s.vertex_count() <= 3

    def test_to_coords(self):
        p = Polyline.from_xy([(0, 0), (1, 1)])
        c = p.to_coords()
        assert c == [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]

    def test_to_coords_2d(self):
        p = Polyline.from_xy([(0, 0), (1, 1)])
        c = p.to_coords_2d()
        assert c == [(0.0, 0.0), (1.0, 1.0)]

    def test_repr(self):
        p = Polyline.from_xy([(0, 0), (1, 0)])
        r = repr(p)
        assert "Polyline" in r

    def test_closed_property(self):
        p = Polyline.from_xy([(0, 0), (1, 0)], closed=True)
        assert p.closed
