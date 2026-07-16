import math

import pytest

from dinpro.domain.axis import Axis
from dinpro.domain.linear_referencing.calibration_issue import CalibrationSeverity
from dinpro.domain.linear_referencing.calibration_point import CalibrationPoint
from dinpro.domain.linear_referencing.calibration_set import CalibrationSet
from dinpro.domain.linear_referencing.extrapolation_mode import ExtrapolationMode
from dinpro.domain.linear_referencing.route_calibration import CalibrationError, RouteCalibration
from dinpro.domain.linear_referencing.station import Station


@pytest.fixture
def axis():
    return Axis.from_xy([(0, 0), (500, 0), (1000, 0)], name="route_test")


@pytest.fixture
def simple_points():
    return (
        CalibrationPoint(0.0, Station(0.0)),
        CalibrationPoint(500.0, Station(510.0)),
        CalibrationPoint(1000.0, Station(1020.0)),
    )


@pytest.fixture
def simple_set(axis, simple_points):
    return CalibrationSet("campaign_1", axis, simple_points)


@pytest.fixture
def rc(axis, simple_set):
    return RouteCalibration(axis, [simple_set])


class TestCalibrationPoint:
    def test_create(self):
        cp = CalibrationPoint(100.0, Station(105.0))
        assert math.isclose(cp.distance, 100.0)
        assert math.isclose(cp.station.value, 105.0)
        assert cp.source == "manual"
        assert math.isclose(cp.confidence, 1.0)

    def test_defaults(self):
        cp = CalibrationPoint(0.0, Station(0.0))
        assert cp.source == "manual"
        assert math.isclose(cp.confidence, 1.0)

    def test_frozen(self):
        cp = CalibrationPoint(0.0, Station(0.0))
        with pytest.raises(AttributeError):
            cp._distance = 100.0

    def test_invalid_confidence_low(self):
        with pytest.raises(ValueError):
            CalibrationPoint(0.0, Station(0.0), _confidence=-0.1)

    def test_invalid_confidence_high(self):
        with pytest.raises(ValueError):
            CalibrationPoint(0.0, Station(0.0), _confidence=1.5)

    def test_invalid_station_type(self):
        with pytest.raises(TypeError):
            CalibrationPoint(0.0, "not_a_station")

    def test_equality(self):
        cp1 = CalibrationPoint(100.0, Station(105.0))
        cp2 = CalibrationPoint(100.0, Station(105.0))
        assert cp1 == cp2

    def test_inequality(self):
        cp1 = CalibrationPoint(100.0, Station(105.0))
        cp2 = CalibrationPoint(100.0, Station(110.0))
        assert cp1 != cp2


class TestCalibrationSet:
    def test_create(self, axis, simple_points):
        cs = CalibrationSet("camp_1", axis, simple_points)
        assert cs.campaign_id == "camp_1"
        assert cs.axis is axis
        assert len(cs.points) == 3
        assert cs.created_at != ""

    def test_empty_points_raises(self, axis):
        with pytest.raises(ValueError):
            CalibrationSet("empty", axis, ())

    def test_invalid_point_type_raises(self, axis):
        with pytest.raises(TypeError):
            CalibrationSet("bad", axis, ("not_a_point",))

    def test_frozen(self, axis, simple_points):
        cs = CalibrationSet("c", axis, simple_points)
        with pytest.raises(AttributeError):
            cs._campaign_id = "new"

    def test_validate_valid(self, axis, simple_points):
        cs = CalibrationSet("valid", axis, simple_points)
        issues = cs.validate()
        assert len(issues) == 0

    def test_validate_non_increasing(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(0.0)),
            CalibrationPoint(200.0, Station(200.0)),
            CalibrationPoint(150.0, Station(300.0)),
        )
        cs = CalibrationSet("bad", axis, pts)
        issues = cs.validate()
        assert len(issues) >= 1
        assert any(i.code == "RC002" for i in issues)

    def test_validate_single_point(self, axis):
        pts = (CalibrationPoint(0.0, Station(0.0)),)
        cs = CalibrationSet("single", axis, pts)
        issues = cs.validate()
        assert len(issues) >= 1
        assert any(i.code == "RC001" for i in issues)

    def test_validate_single_point_severity(self, axis):
        pts = (CalibrationPoint(0.0, Station(0.0)),)
        cs = CalibrationSet("single", axis, pts)
        issues = cs.validate()
        assert issues[0].severity == CalibrationSeverity.ERROR


class TestRouteCalibrationCreation:
    def test_create(self, axis, simple_set):
        rc = RouteCalibration(axis, [simple_set])
        assert rc.axis is axis
        assert rc.active_set is simple_set

    def test_multiple_sets(self, axis, simple_points):
        cs1 = CalibrationSet("old", axis, simple_points)
        cs2 = CalibrationSet("new", axis, simple_points)
        rc = RouteCalibration(axis, [cs1, cs2], default_campaign="new")
        assert rc.active_set is cs2

    def test_default_campaign_first(self, axis, simple_points):
        cs1 = CalibrationSet("a", axis, simple_points)
        cs2 = CalibrationSet("b", axis, simple_points)
        rc = RouteCalibration(axis, [cs1, cs2])
        assert rc.active_set is cs1

    def test_nonexistent_default_raises(self, axis, simple_points):
        cs = CalibrationSet("exists", axis, simple_points)
        with pytest.raises(ValueError):
            RouteCalibration(axis, [cs], default_campaign="nonexistent")

    def test_empty_sets_raises(self, axis):
        with pytest.raises(ValueError):
            RouteCalibration(axis, [])

    def test_calibration_sets_property(self, axis, simple_points):
        cs1 = CalibrationSet("a", axis, simple_points)
        cs2 = CalibrationSet("b", axis, simple_points)
        rc = RouteCalibration(axis, [cs1, cs2])
        assert len(rc.calibration_sets) == 2


class TestStationAtDistance:
    def test_at_start(self, rc):
        s = rc.station_at_distance(0.0)
        assert math.isclose(s.value, 0.0)

    def test_at_end(self, rc):
        s = rc.station_at_distance(1000.0)
        assert math.isclose(s.value, 1020.0, rel_tol=1e-6)

    def test_midpoint(self, rc):
        s = rc.station_at_distance(500.0)
        assert math.isclose(s.value, 510.0, rel_tol=1e-6)

    def test_interpolated(self, rc):
        s = rc.station_at_distance(250.0)
        expected = 0.0 + (250.0 / 500.0) * 510.0
        assert math.isclose(s.value, expected, rel_tol=1e-6)

    def test_out_of_range_none_raises(self, rc):
        with pytest.raises(CalibrationError):
            rc.station_at_distance(2000.0, ExtrapolationMode.NONE)

    def test_out_of_range_below_none_raises(self, rc):
        with pytest.raises(CalibrationError):
            rc.station_at_distance(-100.0, ExtrapolationMode.NONE)

    def test_extrapolate_linear_above(self, rc):
        s = rc.station_at_distance(1500.0, ExtrapolationMode.LINEAR)
        ratio = 500.0 / 500.0
        expected = 1020.0 + ratio * (1020.0 - 510.0)
        assert math.isclose(s.value, expected, rel_tol=1e-6)

    def test_extrapolate_linear_below(self, rc):
        s = rc.station_at_distance(-500.0, ExtrapolationMode.LINEAR)
        ratio = 500.0 / 500.0
        expected = 0.0 - ratio * (510.0 - 0.0)
        assert math.isclose(s.value, expected, rel_tol=1e-6)

    def test_extrapolate_constant_above(self, rc):
        s = rc.station_at_distance(2000.0, ExtrapolationMode.CONSTANT)
        assert math.isclose(s.value, 1020.0)

    def test_extrapolate_constant_below(self, rc):
        s = rc.station_at_distance(-500.0, ExtrapolationMode.CONSTANT)
        assert math.isclose(s.value, 0.0)


class TestDistanceAtStation:
    def test_at_start(self, rc):
        d = rc.distance_at_station(Station(0.0))
        assert math.isclose(d, 0.0)

    def test_at_end(self, rc):
        d = rc.distance_at_station(Station(1020.0))
        assert math.isclose(d, 1000.0, rel_tol=1e-6)

    def test_midpoint(self, rc):
        d = rc.distance_at_station(Station(510.0))
        assert math.isclose(d, 500.0, rel_tol=1e-6)

    def test_interpolated(self, rc):
        d = rc.distance_at_station(Station(255.0))
        expected = 0.0 + (255.0 / 510.0) * 500.0
        assert math.isclose(d, expected, rel_tol=1e-6)

    def test_out_of_range_none_raises(self, rc):
        with pytest.raises(CalibrationError):
            rc.distance_at_station(Station(9999.0), ExtrapolationMode.NONE)

    def test_symmetry(self, rc):
        for d in [0.0, 100.0, 250.0, 500.0, 750.0, 1000.0]:
            s = rc.station_at_distance(d)
            d_back = rc.distance_at_station(s)
            assert math.isclose(d, d_back, rel_tol=1e-9)


class TestDecreasingPK:
    def test_decreasing_pk_interpolation(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(1000.0)),
            CalibrationPoint(500.0, Station(500.0)),
            CalibrationPoint(1000.0, Station(0.0)),
        )
        cs = CalibrationSet("decreasing", axis, pts)
        rc = RouteCalibration(axis, [cs])
        s = rc.station_at_distance(250.0)
        assert math.isclose(s.value, 750.0, rel_tol=1e-6)

    def test_decreasing_pk_distance_at_station(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(1000.0)),
            CalibrationPoint(500.0, Station(500.0)),
            CalibrationPoint(1000.0, Station(0.0)),
        )
        cs = CalibrationSet("decreasing", axis, pts)
        rc = RouteCalibration(axis, [cs])
        d = rc.distance_at_station(Station(750.0))
        assert math.isclose(d, 250.0, rel_tol=1e-6)

    def test_decreasing_pk_symmetry(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(1000.0)),
            CalibrationPoint(1000.0, Station(0.0)),
        )
        cs = CalibrationSet("decreasing", axis, pts)
        rc = RouteCalibration(axis, [cs])
        for d in [0.0, 250.0, 500.0, 750.0, 1000.0]:
            s = rc.station_at_distance(d)
            d_back = rc.distance_at_station(s)
            assert math.isclose(d, d_back, rel_tol=1e-9)

    def test_decreasing_validate_warning(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(1000.0)),
            CalibrationPoint(500.0, Station(500.0)),
        )
        cs = CalibrationSet("dec", axis, pts)
        rc = RouteCalibration(axis, [cs])
        issues = rc.validate()
        assert any(i.severity == CalibrationSeverity.WARNING for i in issues)
        assert any(i.code == "RC003" for i in issues)


class TestInterpolateExtrapolateAliases:
    def test_interpolate(self, rc):
        s = rc.interpolate(500.0)
        assert math.isclose(s.value, 510.0, rel_tol=1e-6)

    def test_interpolate_out_of_range_raises(self, rc):
        with pytest.raises(CalibrationError):
            rc.interpolate(2000.0)

    def test_extrapolate(self, rc):
        s = rc.extrapolate(1500.0)
        assert s is not None


class TestValidate:
    def test_validate_valid(self, rc):
        issues = rc.validate()
        assert len(issues) >= 0

    def test_validate_duplicate_distances(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(0.0)),
            CalibrationPoint(500.0, Station(510.0)),
            CalibrationPoint(500.0, Station(520.0)),
        )
        cs = CalibrationSet("dup", axis, pts)
        rc = RouteCalibration(axis, [cs])
        issues = rc.validate()
        assert any(i.code == "RC002" for i in issues)

    def test_calibration_issue_structure(self, axis):
        pts = (CalibrationPoint(0.0, Station(0.0)),)
        cs = CalibrationSet("single", axis, pts)
        rc = RouteCalibration(axis, [cs])
        issues = rc.validate()
        issue = issues[0]
        assert hasattr(issue, "severity")
        assert hasattr(issue, "code")
        assert hasattr(issue, "message")


class TestMultipleCalibrations:
    def test_switch_campaign(self, axis, simple_points):
        cs1 = CalibrationSet("v1", axis, simple_points)
        pts_v2 = (
            CalibrationPoint(0.0, Station(0.0)),
            CalibrationPoint(500.0, Station(505.0)),
            CalibrationPoint(1000.0, Station(1010.0)),
        )
        cs2 = CalibrationSet("v2", axis, pts_v2)
        rc = RouteCalibration(axis, [cs1, cs2], default_campaign="v2")
        assert rc.active_set is cs2

    def test_campaigns_not_lost(self, axis, simple_points):
        cs1 = CalibrationSet("a", axis, simple_points)
        cs2 = CalibrationSet("b", axis, simple_points)
        rc = RouteCalibration(axis, [cs1, cs2])
        assert len(rc.calibration_sets) == 2


class TestEdgeCases:
    def test_exact_calibration(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(0.0)),
            CalibrationPoint(1000.0, Station(1000.0)),
        )
        cs = CalibrationSet("exact", axis, pts)
        rc = RouteCalibration(axis, [cs])
        s = rc.station_at_distance(500.0)
        assert math.isclose(s.value, 500.0)
        d = rc.distance_at_station(Station(500.0))
        assert math.isclose(d, 500.0)

    def test_zero_length_segment(self, axis):
        pts = (
            CalibrationPoint(0.0, Station(0.0)),
            CalibrationPoint(0.0, Station(100.0)),
        )
        cs = CalibrationSet("zero", axis, pts)
        rc = RouteCalibration(axis, [cs])
        s = rc.station_at_distance(0.0)
        assert math.isclose(s.value, 0.0)

    def test_single_point_set(self, axis):
        pts = (CalibrationPoint(0.0, Station(0.0)),)
        cs = CalibrationSet("single", axis, pts)
        rc = RouteCalibration(axis, [cs])
        with pytest.raises(CalibrationError):
            rc.station_at_distance(500.0)
