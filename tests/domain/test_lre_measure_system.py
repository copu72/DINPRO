import math
import pytest
from dinpro.domain.linear_referencing.measure_system import (
    CalibrationPoint,
    MeasureDiscontinuity,
    MeasureSystem,
)
from dinpro.domain.axis import Axis


class TestCalibrationPoint:
    def test_creation(self):
        cp = CalibrationPoint(pk=1000.0, distance=998.5)
        assert cp.pk == 1000.0
        assert cp.distance == 998.5


class TestMeasureDiscontinuity:
    def test_creation(self):
        md = MeasureDiscontinuity(start_pk=5000.0, end_pk=5000.0, gap_before=50.0)
        assert md.start_pk == 5000.0
        assert md.gap_before == 50.0


class TestMeasureSystem:
    @pytest.fixture
    def axis(self):
        return Axis.from_xy([(0, 0), (1000, 0)], name="test")

    @pytest.fixture
    def system(self, axis):
        return MeasureSystem(axis=axis)

    def test_default_measure_equals_distance(self, axis):
        ms = MeasureSystem(axis=axis)
        assert math.isclose(ms.pk_at_distance(500.0), 500.0)
        assert math.isclose(ms.distance_at_pk(500.0), 500.0)

    def test_without_axis(self):
        ms = MeasureSystem()
        assert math.isclose(ms.pk_at_distance(100.0), 100.0)

    def test_calibrate_single_point(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=500.0, distance=500.0)])
        assert ms.is_calibrated

    def test_calibrate_before_point(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=100.0, distance=100.0)])
        assert math.isclose(ms.pk_at_distance(50.0), 50.0)

    def test_calibrate_after_point(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=100.0, distance=100.0)])
        assert math.isclose(ms.pk_at_distance(200.0), 200.0)

    def test_calibrate_interpolated(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=0.0, distance=0.0),
            CalibrationPoint(pk=500.0, distance=500.0),
        ])
        assert math.isclose(ms.pk_at_distance(250.0), 250.0)

    def test_calibrate_with_offset(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=1000.0, distance=0.0),
            CalibrationPoint(pk=2000.0, distance=1000.0),
        ])
        assert math.isclose(ms.pk_at_distance(0.0), 1000.0)
        assert math.isclose(ms.pk_at_distance(500.0), 1500.0)

    def test_distance_at_pk_with_offset(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=1000.0, distance=0.0),
            CalibrationPoint(pk=2000.0, distance=1000.0),
        ])
        assert math.isclose(ms.distance_at_pk(1000.0), 0.0)
        assert math.isclose(ms.distance_at_pk(1500.0), 500.0)
        assert math.isclose(ms.distance_at_pk(2000.0), 1000.0)

    def test_total_measure_without_calibration(self, axis):
        ms = MeasureSystem(axis=axis)
        assert math.isclose(ms.total_measure(), 1000.0)

    def test_total_measure_with_calibration(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=0.0, distance=0.0),
            CalibrationPoint(pk=1100.0, distance=1000.0),
        ])
        assert math.isclose(ms.total_measure(), 1100.0)

    def test_total_measure_without_axis(self):
        ms = MeasureSystem()
        assert ms.total_measure() == 0.0

    def test_total_measure_with_calibrations_no_axis(self):
        ms = MeasureSystem(calibrations=[
            CalibrationPoint(pk=500.0, distance=500.0),
        ])
        assert math.isclose(ms.total_measure(), 500.0)

    def test_validate_clean(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=0.0, distance=0.0),
            CalibrationPoint(pk=1000.0, distance=1000.0),
        ])
        assert len(ms.validate()) == 0

    def test_validate_deviation_warning(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([
            CalibrationPoint(pk=0.0, distance=0.0),
            CalibrationPoint(pk=950.0, distance=1000.0),
        ])
        warnings = ms.validate()
        assert len(warnings) > 0

    def test_add_discontinuity(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.add_discontinuity(500.0, 50.0)
        assert len(ms.discontinuities) == 1
        assert ms.discontinuities[0].gap_before == 50.0

    def test_calibrate_negative_pk_raises(self, axis):
        ms = MeasureSystem(axis=axis)
        with pytest.raises(ValueError):
            ms.calibrate([CalibrationPoint(pk=-1.0, distance=0.0)])

    def test_clear(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=100.0, distance=100.0)])
        assert ms.is_calibrated
        ms.clear()
        assert not ms.is_calibrated

    def test_is_calibrated_false_by_default(self, axis):
        ms = MeasureSystem(axis=axis)
        assert not ms.is_calibrated

    def test_calibrations_property(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=100.0, distance=100.0)])
        assert len(ms.calibrations) == 1

    def test_discontinuities_property(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.add_discontinuity(500.0, 50.0)
        assert len(ms.discontinuities) == 1

    def test_calibrate_replaces_existing(self, axis):
        ms = MeasureSystem(axis=axis)
        ms.calibrate([CalibrationPoint(pk=100.0, distance=100.0)])
        ms.calibrate([CalibrationPoint(pk=100.0, distance=105.0)])
        cp = [c for c in ms.calibrations if c.pk == 100.0][0]
        assert math.isclose(cp.distance, 105.0)

    def test_validate_no_warnings_empty(self, axis):
        ms = MeasureSystem(axis=axis)
        assert len(ms.validate()) == 0
