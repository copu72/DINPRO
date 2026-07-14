import math

import pytest

from dinpro.domain.axis import Axis
from dinpro.domain.geometry.polygon import Polygon
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.linear_referencing.dynamic_segmentation import DynamicSegmentation
from dinpro.domain.linear_referencing.segment import Segment, _extract_subpolyline
from dinpro.domain.linear_referencing.station import Station


@pytest.fixture
def axis():
    return Axis.from_xy(
        [(0, 0), (250, 0), (500, 100), (750, 100), (1000, 0)], name="test"
    )


@pytest.fixture
def ds(axis):
    return DynamicSegmentation(axis)


class TestSegmentCreation:
    def test_create(self, axis):
        s = Segment(
            _axis=axis,
            _start=Station(100.0),
            _end=Station(500.0),
            _geometry=Polyline.from_xy([(100, 0), (250, 0), (500, 100)]),
        )
        assert s.axis == axis
        assert math.isclose(s.station_start.value, 100.0)
        assert math.isclose(s.station_end.value, 500.0)
        assert s.length > 0

    def test_inverted_raises(self, axis):
        with pytest.raises(ValueError):
            Segment(
                _axis=axis,
                _start=Station(500.0),
                _end=Station(100.0),
                _geometry=Polyline.from_xy([(100, 0), (250, 0)]),
            )

    def test_zero_length_raises(self, axis):
        with pytest.raises(ValueError):
            Segment(
                _axis=axis,
                _start=Station(100.0),
                _end=Station(100.0),
                _geometry=Polyline.from_xy([(100, 0), (100, 0)]),
            )


class TestDynamicSegmentationCreate:
    def test_full_axis_segment(self, ds):
        end = ds.axis.length
        s = ds.segment(Station(0.0), Station(end))
        assert math.isclose(s.length, end, rel_tol=1e-3)
        assert math.isclose(s.station_start.value, 0.0)
        assert math.isclose(s.station_end.value, end)

    def test_central_segment(self, ds):
        s = ds.segment(Station(100.0), Station(400.0))
        assert s.length > 0
        assert math.isclose(s.station_start.value, 100.0)
        assert math.isclose(s.station_end.value, 400.0)

    def test_very_small_segment(self, ds):
        s = ds.segment(Station(100.0), Station(101.0))
        assert s.length > 0

    def test_inverted_raises(self, ds):
        with pytest.raises(ValueError):
            ds.segment(Station(500.0), Station(100.0))


class TestSegmentProperties:
    def test_id_is_unique(self, axis):
        p = Polyline.from_xy([(0, 0), (100, 0)])
        s1 = Segment(_axis=axis, _start=Station(0), _end=Station(100), _geometry=p)
        s2 = Segment(_axis=axis, _start=Station(0), _end=Station(100), _geometry=p)
        assert s1.id != s2.id

    def test_attributes(self, axis):
        p = Polyline.from_xy([(0, 0), (100, 0)])
        s = Segment(
            _axis=axis,
            _start=Station(0),
            _end=Station(100),
            _geometry=p,
            _attributes={"name": "test", "type": "segment"},
        )
        assert s.attributes["name"] == "test"


class TestSegmentReverse:
    def test_reverse_preserves_stations(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        r = s.reverse()
        assert math.isclose(r.station_start.value, 100.0)
        assert math.isclose(r.station_end.value, 500.0)

    def test_reverse_immutable(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        orig_len = s.length
        r = s.reverse()
        assert s is not r
        assert math.isclose(s.length, orig_len)

    def test_reverse_geometry_differs(self, ds):
        s = ds.segment(Station(0.0), Station(200.0))
        r = s.reverse()
        sv = [(p.x, p.y) for p in s.geometry.vertices]
        rv = [(p.x, p.y) for p in r.geometry.vertices]
        assert sv == rv[::-1]


class TestSegmentContains:
    def test_contains_middle(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        assert s.contains(Station(300.0))

    def test_contains_start(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        assert s.contains(Station(100.0))

    def test_contains_end(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        assert s.contains(Station(500.0))

    def test_not_contains_before(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        assert not s.contains(Station(50.0))

    def test_not_contains_after(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        assert not s.contains(Station(600.0))


class TestSegmentIntersects:
    def test_overlapping(self, ds):
        s1 = ds.segment(Station(100.0), Station(400.0))
        s2 = ds.segment(Station(300.0), Station(600.0))
        assert s1.intersects(s2)

    def test_non_overlapping(self, ds):
        s1 = ds.segment(Station(100.0), Station(200.0))
        s2 = ds.segment(Station(300.0), Station(400.0))
        assert not s1.intersects(s2)

    def test_touching(self, ds):
        s1 = ds.segment(Station(100.0), Station(200.0))
        s2 = ds.segment(Station(200.0), Station(300.0))
        assert not s1.intersects(s2)


class TestSegmentToAxis:
    def test_to_axis_returns_axis(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        sub = s.to_axis()
        assert sub is not None
        assert sub.length > 0
        assert s.axis.name in sub.name


class TestSegmentOffset:
    def test_offset_returns_polygon(self, ds):
        s = ds.segment(Station(100.0), Station(400.0))
        corr = s.offset(25)
        assert isinstance(corr, Polygon)

    def test_offset_right(self, ds):
        s = ds.segment(Station(100.0), Station(400.0))
        corr = s.offset(25)
        assert isinstance(corr, Polygon)


class TestSegmentClip:
    def test_clip_narrower(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        clipped = s.clip(Station(200.0), Station(400.0))
        assert math.isclose(clipped.station_start.value, 200.0)
        assert math.isclose(clipped.station_end.value, 400.0)
        assert clipped.length < s.length

    def test_clip_same(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        clipped = s.clip(Station(100.0), Station(500.0))
        assert math.isclose(clipped.length, s.length, rel_tol=1e-3)

    def test_clip_invalid_raises(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        with pytest.raises(ValueError):
            s.clip(Station(400.0), Station(200.0))

    def test_clip_immutable(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        orig_len = s.length
        s.clip(Station(200.0), Station(400.0))
        assert math.isclose(s.length, orig_len)


class TestSplit:
    def test_split_at_mid(self, ds):
        segs = ds.split([Station(500.0)])
        assert len(segs) >= 2
        assert all(s.length > 0 for s in segs)

    def test_split_at_multiple(self, ds):
        segs = ds.split([Station(250.0), Station(500.0), Station(750.0)])
        assert len(segs) >= 4
        total = sum(s.length for s in segs)
        assert math.isclose(total, ds.axis.length, rel_tol=1e-3)

    def test_split_empty_returns_full(self, ds):
        segs = ds.split([])
        assert len(segs) == 1
        assert math.isclose(segs[0].length, ds.axis.length, rel_tol=1e-3)

    def test_split_consecutive_no_gaps(self, ds):
        segs = ds.split([Station(200.0), Station(500.0), Station(800.0)])
        for i in range(len(segs) - 1):
            assert math.isclose(
                segs[i].station_end.value,
                segs[i + 1].station_start.value,
            )

    def test_split_preserves_total_length(self, ds):
        segs = ds.split([Station(300.0), Station(700.0)])
        total = sum(s.length for s in segs)
        whole = ds.segment(Station(0.0), Station(ds.axis.length))
        assert math.isclose(total, whole.length, rel_tol=1e-3)


class TestMerge:
    def test_merge_two_contiguous(self, ds):
        segs = ds.split([Station(500.0)])
        merged = DynamicSegmentation.merge(segs)
        assert math.isclose(merged.length, ds.axis.length, rel_tol=1e-3)

    def test_merge_preserves_start_end(self, ds):
        segs = ds.split([Station(300.0), Station(700.0)])
        merged = DynamicSegmentation.merge(segs)
        assert math.isclose(merged.station_start.value, 0.0)
        assert math.isclose(merged.station_end.value, ds.axis.length, rel_tol=1e-3)

    def test_merge_empty_raises(self, ds):
        with pytest.raises(ValueError):
            DynamicSegmentation.merge([])


class TestSplitMergeRoundtrip:
    def test_split_merge_preserves_length(self, ds):
        stations = [Station(200.0), Station(500.0), Station(800.0)]
        segs = ds.split(stations)
        merged = DynamicSegmentation.merge(segs)
        original = ds.segment(Station(0.0), Station(ds.axis.length))
        assert math.isclose(merged.length, original.length, rel_tol=1e-3)

    def test_split_merge_stations_match(self, ds):
        stations = [Station(250.0), Station(500.0), Station(750.0)]
        segs = ds.split(stations)
        merged = DynamicSegmentation.merge(segs)
        assert math.isclose(merged.station_start.value, 0.0)
        assert math.isclose(merged.station_end.value, ds.axis.length, rel_tol=1e-3)


class TestSegmentImmutability:
    def test_reverse_does_not_modify(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        orig_start = s.station_start.value
        orig_end = s.station_end.value
        s.reverse()
        assert math.isclose(s.station_start.value, orig_start)
        assert math.isclose(s.station_end.value, orig_end)

    def test_clip_does_not_modify(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        orig_len = s.length
        s.clip(Station(200.0), Station(300.0))
        assert math.isclose(s.length, orig_len)


class TestExtractSubpolyline:
    def test_extract_full(self):
        p = Polyline.from_xy([(0, 0), (100, 0), (200, 0)])
        sub = _extract_subpolyline(p, 0.0, 200.0)
        assert math.isclose(sub.length(), 200.0, rel_tol=1e-6)

    def test_extract_partial(self):
        p = Polyline.from_xy([(0, 0), (100, 0), (200, 0)])
        sub = _extract_subpolyline(p, 50.0, 150.0)
        assert math.isclose(sub.length(), 100.0, rel_tol=1e-6)

    def test_extract_invalid_raises(self):
        p = Polyline.from_xy([(0, 0), (100, 0)])
        with pytest.raises(ValueError):
            _extract_subpolyline(p, 100.0, 50.0)


class TestEdgeCases:
    def test_zero_length_subpolyline_raises(self, axis):
        with pytest.raises(ValueError):
            _extract_subpolyline(axis.polyline, 500.0, 500.0)

    def test_split_at_boundary(self, ds):
        segs = ds.split([Station(0.0)])
        assert len(segs) >= 1

    def test_split_at_end(self, ds):
        segs = ds.split([Station(1000.0)])
        assert len(segs) >= 1

    def test_segment_then_offset(self, ds):
        s = ds.segment(Station(100.0), Station(500.0))
        corr = s.offset(50)
        assert isinstance(corr, Polygon)
        assert len(corr.vertices) > 0
