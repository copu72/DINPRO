import math
import pytest
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.linear_referencing import LinearReferencing, PK


class TestLinearReferencing:
    @pytest.fixture
    def ref(self):
        poly = Polyline.from_xy([(0, 0), (10, 0), (10, 10)])
        return LinearReferencing(poly)

    def test_length(self, ref):
        assert math.isclose(ref.length, 20.0)

    def test_point_at_pk(self, ref):
        p = ref.point_at_pk(PK(5))
        assert p == Point(5, 0)

    def test_pk_at_point(self, ref):
        pk = ref.pk_at_point(Point(5, 0))
        assert math.isclose(pk.value, 5.0)

    def test_pk_from_distance(self, ref):
        pk = ref.pk_from_distance(15.0)
        assert pk.value == 15.0

    def test_station_at_pk(self, ref):
        station = ref.station_at_pk(PK(25350))
        assert station.to_pk_string() == "PK 25+350"

    def test_tangent_at_pk(self, ref):
        t = ref.tangent_at_pk(PK(5))
        assert math.isclose(t.x, 1.0)
        assert math.isclose(t.y, 0.0)

    def test_normal_at_pk(self, ref):
        n = ref.normal_at_pk(PK(5))
        assert math.isclose(n.x, 0.0)
        assert math.isclose(n.y, 1.0)

    def test_azimuth_at_pk(self, ref):
        az = ref.azimuth_at_pk(PK(5))
        assert math.isclose(az, 0.0)

    def test_azimuth_at_pk_second_segment(self, ref):
        az = ref.azimuth_at_pk(PK(15))
        assert math.isclose(az, 90.0)

    def test_slope(self, ref):
        s = ref.slope_at_pk(PK(5))
        assert math.isclose(s, 0.0)

    def test_curvature(self, ref):
        poly = Polyline.from_xy([(0, 0), (1, 0), (2, 0)])
        lr = LinearReferencing(poly)
        c = lr.curvature_at_pk(PK(1))
        assert math.isclose(c, 0.0)

    def test_point_at_distance(self, ref):
        p = ref.point_at_distance(5)
        assert p == Point(5, 0)

    def test_nearest_point(self, ref):
        np, pk, dist = ref.nearest_point(Point(5, 3))
        assert np == Point(5, 0)
        assert dist == 3.0

    def test_project(self, ref):
        np, pk, dist = ref.project(Point(5, 3))
        assert np == Point(5, 0)

    def test_stationing(self, ref):
        stations = ref.stationing()
        assert len(stations) == 3
        assert stations[0][0].value == 0.0
        assert stations[1][0].value == 10.0
        assert stations[2][0].value == 20.0

    def test_segment_at_pk(self, ref):
        seg = ref.segment_at_pk(PK(5))
        assert seg.start == Point(0, 0)
        assert seg.end == Point(10, 0)
