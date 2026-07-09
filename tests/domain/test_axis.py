import math
import pytest
from dinpro.domain.axis import Axis
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.geometry.bounding_box import BoundingBox
from dinpro.domain.crs import CRSRegistry
from dinpro.domain.linear_referencing.pk import PK


class TestAxis:
    @pytest.fixture
    def axis(self):
        return Axis.from_xy([(0, 0), (10, 0), (10, 10)], name="test_axis")

    def test_creation(self, axis):
        assert axis.name == "test_axis"
        assert axis.vertex_count == 3

    def test_from_coords(self):
        axis = Axis.from_coords([(0, 0, 0), (10, 0, 0)], name="3d")
        assert axis.vertex_count == 2

    def test_length(self, axis):
        assert math.isclose(axis.length, 20.0)

    def test_length_2d(self, axis):
        assert math.isclose(axis.length_2d, 20.0)

    def test_vertices(self, axis):
        verts = axis.vertices
        assert len(verts) == 3

    def test_vertex(self, axis):
        v = axis.vertex(0)
        assert v == Point(0, 0)

    def test_closed(self, axis):
        assert not axis.closed

    def test_segments(self, axis):
        segs = axis.segments()
        assert len(segs) == 2

    def test_segment(self, axis):
        seg = axis.segment(0)
        assert seg.start == Point(0, 0)
        assert seg.end == Point(10, 0)

    def test_bounding_box(self, axis):
        bb = axis.bounding_box()
        assert bb.xmin == 0
        assert bb.ymax == 10

    def test_centroid(self, axis):
        c = axis.centroid()
        assert c == Point(20/3, 10/3, 0)

    def test_point_at(self, axis):
        p = axis.point_at(5)
        assert p == Point(5, 0)

    def test_point_at_pk_float(self, axis):
        p = axis.point_at_pk(5.0)
        assert p == Point(5, 0)

    def test_point_at_pk_string(self, axis):
        p = axis.point_at_pk("PK 0+005")
        assert p == Point(5, 0)

    def test_point_at_pk_object(self, axis):
        p = axis.point_at_pk(PK(5))
        assert p == Point(5, 0)

    def test_pk_at_point(self, axis):
        pk = axis.pk_at_point(Point(5, 0))
        assert math.isclose(pk.value, 5.0)

    def test_pk_from_distance(self, axis):
        pk = axis.pk_from_distance(15)
        assert pk.value == 15.0

    def test_pk_create(self, axis):
        pk = axis.pk(1000)
        assert pk.value == 1000.0
        pk = axis.pk("PK 1+000")
        assert pk.value == 1000.0
        pk = axis.pk()
        assert pk.value == 0.0

    def test_stationing(self, axis):
        stations = axis.stationing()
        assert len(stations) == 3

    def test_azimuth(self, axis):
        az = axis.azimuth(0)
        assert math.isclose(az, 0.0)

    def test_azimuth_default(self, axis):
        az = axis.azimuth()
        assert math.isclose(az, 0.0)

    def test_tangent(self, axis):
        t = axis.tangent(0)
        assert math.isclose(t.x, 1.0)

    def test_normal(self, axis):
        n = axis.normal(0)
        assert math.isclose(n.y, 1.0)

    def test_slope(self, axis):
        s = axis.slope(0)
        assert math.isclose(s, 0.0)

    def test_curvature(self, axis):
        c = axis.curvature(5)
        assert math.isclose(c, 0.0)

    def test_nearest_point(self, axis):
        np, pk, dist = axis.nearest_point(Point(5, 3))
        assert math.isclose(dist, 3.0)

    def test_project(self, axis):
        np, pk, dist = axis.project(Point(5, 3))
        assert math.isclose(dist, 3.0)

    def test_buffer(self, axis):
        buf = axis.buffer(2.0)
        assert buf.vertex_count == 3

    def test_offset(self, axis):
        off = axis.offset(2.0)
        assert off.vertex_count == 3

    def test_split(self, axis):
        left, right = axis.split(Point(5, 0))
        assert math.isclose(left.length, 5.0)
        assert math.isclose(right.length, 15.0)

    def test_split_at_pk(self, axis):
        left, right = axis.split_at_pk(5)
        assert math.isclose(left.length, 5.0)

    def test_merge(self, axis):
        a = Axis.from_xy([(0, 0), (5, 0)])
        b = Axis.from_xy([(5, 0), (10, 0)])
        merged = a.merge(b)
        assert math.isclose(merged.length, 10.0)

    def test_clip(self, axis):
        bbox = BoundingBox(2, -1, 8, 1)
        clipped = axis.clip(bbox)
        assert clipped.vertex_count >= 2

    def test_reverse(self, axis):
        rev = axis.reverse()
        assert rev.vertex(0) == Point(10, 10)

    def test_simplify(self, axis):
        simp = axis.simplify(0.1)
        assert simp.vertex_count <= 3

    def test_transform_no_crs(self, axis):
        with pytest.raises(ValueError):
            axis.transform(CRSRegistry.get("WGS84"))

    def test_export_dict(self, axis):
        d = axis.export("dict")
        assert d["name"] == "test_axis"
        assert d["length"] == 20.0
        assert len(d["vertices"]) == 3

    def test_export_coords(self, axis):
        coords = axis.export("coords")
        assert len(coords) == 3

    def test_export_coords_2d(self, axis):
        coords = axis.export("coords_2d")
        assert len(coords) == 3

    def test_export_invalid(self, axis):
        with pytest.raises(ValueError):
            axis.export("invalid")

    def test_repr(self, axis):
        r = repr(axis)
        assert "Axis" in r

    def test_with_crs(self):
        crs = CRSRegistry.get("ETRS89/UTM30N")
        axis = Axis.from_xy([(0, 0), (1, 0)], crs=crs, name="crs_axis")
        assert axis.crs == crs
