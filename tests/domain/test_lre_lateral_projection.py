import math

import pytest

from dinpro.domain.axis import Axis
from dinpro.domain.geometry.point import Point
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.lateral.lateral_projection import LateralProjection


@pytest.fixture
def horizontal_axis():
    return Axis.from_xy([(0, 0), (1000, 0)], name="horizontal")


@pytest.fixture
def vertical_axis():
    return Axis.from_xy([(0, 0), (0, 1000)], name="vertical")


@pytest.fixture
def diagonal_axis():
    return Axis.from_xy([(0, 0), (1000, 1000)], name="diagonal")


@pytest.fixture
def proj_h(horizontal_axis):
    return LateralProjection(horizontal_axis)


class TestLateralProjectionCreation:
    def test_creation(self, horizontal_axis):
        lp = LateralProjection(horizontal_axis)
        assert lp.axis == horizontal_axis

    def test_axis_property(self, proj_h):
        assert proj_h.axis is not None

    def test_invalid_axis_raises(self):
        with pytest.raises(ValueError):
            Axis.from_xy([(0, 0)], name="single")


class TestOffsetPoint:
    def test_offset_left_horizontal(self, proj_h):
        p = proj_h.offset_point(pk=500.0, distance=10.0, side="left")
        assert math.isclose(p.x, 500.0)
        assert math.isclose(p.y, 10.0)

    def test_offset_right_horizontal(self, proj_h):
        p = proj_h.offset_point(pk=500.0, distance=10.0, side="right")
        assert math.isclose(p.x, 500.0)
        assert math.isclose(p.y, -10.0)

    def test_offset_zero_distance(self, proj_h):
        p = proj_h.offset_point(pk=500.0, distance=0.0, side="left")
        assert math.isclose(p.x, 500.0)
        assert math.isclose(p.y, 0.0)

    @pytest.mark.parametrize("side", ["left", "right"])
    def test_offset_vertical(self, vertical_axis, side):
        lp = LateralProjection(vertical_axis)
        p = lp.offset_point(pk=500.0, distance=10.0, side=side)
        assert math.isclose(p.y, 500.0)
        if side == "left":
            assert math.isclose(p.x, -10.0)
        else:
            assert math.isclose(p.x, 10.0)

    @pytest.mark.parametrize("side", ["left", "right"])
    def test_offset_diagonal(self, diagonal_axis, side):
        lp = LateralProjection(diagonal_axis)
        p = lp.offset_point(pk=500.0, distance=10.0, side=side)
        c = math.cos(math.pi / 4)
        s = math.sin(math.pi / 4)
        offset = 10.0 if side == "left" else -10.0
        assert math.isclose(p.x, 500 * c + (-s) * offset, rel_tol=1e-6)
        assert math.isclose(p.y, 500 * s + c * offset, rel_tol=1e-6)

    def test_offset_pk_start(self, proj_h):
        p = proj_h.offset_point(pk=0.0, distance=5.0, side="left")
        assert math.isclose(p.x, 0.0)
        assert math.isclose(p.y, 5.0)

    def test_offset_pk_end(self, proj_h):
        p = proj_h.offset_point(pk=1000.0, distance=5.0, side="left")
        assert math.isclose(p.x, 1000.0)
        assert math.isclose(p.y, 5.0)


class TestCrossSection:
    def test_cross_section_horizontal(self, proj_h):
        cs = proj_h.cross_section(pk=500.0, left_width=20.0, right_width=30.0)
        assert math.isclose(cs["center"].x, 500.0)
        assert math.isclose(cs["center"].y, 0.0)
        assert math.isclose(cs["left"].x, 500.0)
        assert math.isclose(cs["left"].y, 20.0)
        assert math.isclose(cs["right"].x, 500.0)
        assert math.isclose(cs["right"].y, -30.0)
        assert math.isclose(cs["azimuth"], 0.0)

    def test_cross_section_contains_keys(self, proj_h):
        cs = proj_h.cross_section(pk=500.0)
        assert "center" in cs
        assert "left" in cs
        assert "right" in cs
        assert "pk" in cs
        assert "azimuth" in cs

    def test_cross_section_line(self, proj_h):
        left, right = proj_h.cross_section_line(pk=500.0, left_width=15.0, right_width=25.0)
        assert math.isclose(left.x, 500.0)
        assert math.isclose(left.y, 15.0)
        assert math.isclose(right.x, 500.0)
        assert math.isclose(right.y, -25.0)

    def test_cross_section_default_widths(self, proj_h):
        cs = proj_h.cross_section(pk=500.0)
        assert math.isclose(cs["left"].y, 10.0)
        assert math.isclose(cs["right"].y, -10.0)


class TestCorridor:
    def test_corridor_returns_polygon(self, proj_h):
        corr = proj_h.corridor(pk_start=100.0, pk_end=200.0, half_width=25.0, steps=10)
        assert isinstance(corr, Polygon)

    def test_corridor_vertices_count(self, proj_h):
        corr = proj_h.corridor(pk_start=100.0, pk_end=200.0, half_width=25.0, steps=10)
        assert len(corr.vertices) == 22

    def test_corridor_zero_start(self, proj_h):
        corr = proj_h.corridor(pk_start=0.0, pk_end=500.0, half_width=50.0, steps=20)
        assert isinstance(corr, Polygon)
        assert len(corr.vertices) > 0

    def test_corridor_invalid_range_raises(self, proj_h):
        with pytest.raises(ValueError):
            proj_h.corridor(pk_start=500.0, pk_end=100.0)

    def test_corridor_vertices_invalid_range_raises(self, proj_h):
        with pytest.raises(ValueError):
            proj_h.corridor_vertices(pk_start=500.0, pk_end=100.0)

    def test_corridor_vertices(self, proj_h):
        vertices = proj_h.corridor_vertices(pk_start=0.0, pk_end=100.0, half_width=50.0, steps=5)
        assert "center" in vertices
        assert "left" in vertices
        assert "right" in vertices
        assert len(vertices["center"]) == 6
        assert len(vertices["left"]) == 6
        assert len(vertices["right"]) == 6


class TestMargins:
    def test_margins_returns_dict_with_points(self, proj_h):
        m = proj_h.margins(pk=500.0)
        assert "center" in m
        assert isinstance(m["center"], Point)

    def test_margins_default(self, proj_h):
        m = proj_h.margins(pk=500.0)
        assert math.isclose(m["center"].x, 500.0)


class TestNearestPK:
    def test_nearest_pk_on_axis(self, proj_h):
        pk_val, dist = proj_h.nearest_pk(Point(500, 0))
        assert math.isclose(pk_val, 500.0)
        assert math.isclose(dist, 0.0)

    def test_nearest_pk_off_axis(self, proj_h):
        pk_val, dist = proj_h.nearest_pk(Point(500, 50))
        assert math.isclose(pk_val, 500.0)
        assert math.isclose(dist, 50.0)

    def test_nearest_pk_before_axis(self, proj_h):
        pk_val, dist = proj_h.nearest_pk(Point(-100, 0))
        assert math.isclose(pk_val, 0.0)

    def test_nearest_pk_after_axis(self, proj_h):
        pk_val, dist = proj_h.nearest_pk(Point(2000, 0))
        assert math.isclose(pk_val, 1000.0)


class TestProjectToAxis:
    def test_project_returns_all_keys(self, proj_h):
        result = proj_h.project_to_axis(Point(500, 50))
        assert "point" in result
        assert "pk" in result
        assert "distance" in result
        assert "azimuth" in result
        assert "side" in result

    def test_project_side_left(self, proj_h):
        result = proj_h.project_to_axis(Point(500, 50))
        assert result["side"] == "left"

    def test_project_side_right(self, proj_h):
        result = proj_h.project_to_axis(Point(500, -50))
        assert result["side"] == "right"

    def test_project_on_axis(self, proj_h):
        result = proj_h.project_to_axis(Point(500, 0))
        assert result["side"] == "left"

    def test_project_distance(self, proj_h):
        result = proj_h.project_to_axis(Point(500, 30))
        assert math.isclose(result["distance"], 30.0)


class TestPKResolution:
    def test_pk_none_defaults_to_zero(self, proj_h):
        p = proj_h.offset_point(pk=None, distance=5.0, side="left")
        assert math.isclose(p.x, 0.0)
        assert math.isclose(p.y, 5.0)

    def test_pk_as_float(self, proj_h):
        p = proj_h.offset_point(pk=500.0, distance=5.0, side="left")
        assert math.isclose(p.x, 500.0)

    def test_pk_as_string(self, proj_h):
        p = proj_h.offset_point(pk="0+500", distance=5.0, side="left")
        assert math.isclose(p.y, 5.0)

    def test_pk_as_station(self, proj_h):
        from dinpro.domain.linear_referencing.station import Station
        p = proj_h.offset_point(pk=Station(500), distance=5.0, side="left")
        assert math.isclose(p.y, 5.0)


class TestEdgeCases:
    def test_offset_large_distance(self, proj_h):
        p = proj_h.offset_point(pk=500.0, distance=1000.0, side="left")
        assert math.isclose(p.x, 500.0)
        assert math.isclose(p.y, 1000.0)

    def test_corridor_full_length(self, proj_h):
        corr = proj_h.corridor(pk_start=0.0, pk_end=1000.0, half_width=50.0, steps=50)
        assert isinstance(corr, Polygon)

    def test_corridor_single_step(self, proj_h):
        corr = proj_h.corridor(pk_start=0.0, pk_end=100.0, half_width=10.0, steps=1)
        assert len(corr.vertices) >= 3
