import math

import pytest

from dinpro.domain.axis import Axis
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.linear_referencing.event_type import EventSource, EventType
from dinpro.domain.linear_referencing.linear_event_set import LinearEventSet
from dinpro.domain.linear_referencing.segment import Segment
from dinpro.domain.linear_referencing.station import Station


@pytest.fixture
def axis():
    return Axis.from_xy([(0, 0), (500, 0), (1000, 0)], name="test_axis")


@pytest.fixture
def les(axis):
    return LinearEventSet(axis)


@pytest.fixture
def seg_100_500(axis):
    return Segment(
        _axis=axis,
        _start=Station(100.0),
        _end=Station(500.0),
        _geometry=Polyline.from_xy([(100, 0), (300, 0), (500, 0)]),
    )


@pytest.fixture
def seg_600_900(axis):
    return Segment(
        _axis=axis,
        _start=Station(600.0),
        _end=Station(900.0),
        _geometry=Polyline.from_xy([(600, 0), (750, 0), (900, 0)]),
    )


class TestLinearEventSetCreation:
    def test_create(self, axis):
        les = LinearEventSet(axis)
        assert les.axis is axis
        assert les.count == 0
        assert les.events == []

    def test_different_axis(self):
        a1 = Axis.from_xy([(0, 0), (100, 0)], name="a1")
        a2 = Axis.from_xy([(0, 0), (200, 0)], name="a2")
        les1 = LinearEventSet(a1)
        les2 = LinearEventSet(a2)
        assert les1.axis is a1
        assert les2.axis is a2

    def test_repr(self, les):
        r = repr(les)
        assert "LinearEventSet" in r
        assert "events=0" in r


class TestAdd:
    def test_add_minimal(self, les):
        e = les.add(EventType.UNDEFINED)
        assert e.event_id != ""
        assert e.event_type == EventType.UNDEFINED
        assert les.count == 1

    def test_add_with_segment(self, les, seg_100_500):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        assert e.segment is seg_100_500
        assert math.isclose(e.station_start.value, 100.0)

    def test_add_with_attributes(self, les):
        e = les.add(EventType.UNDEFINED, attributes={"name": "test", "value": 42})
        assert e.attributes["name"] == "test"
        assert e.attributes["value"] == 42

    def test_add_with_source(self, les):
        e = les.add(EventType.UNDEFINED, source=EventSource.API)
        assert e.metadata.source == EventSource.API

    def test_add_default_source(self, les):
        e = les.add(EventType.UNDEFINED)
        assert e.metadata.source == EventSource.MANUAL

    def test_add_increments_count(self, les):
        les.add(EventType.UNDEFINED)
        les.add(EventType.UNDEFINED)
        assert les.count == 2

    def test_add_unique_ids(self, les):
        e1 = les.add(EventType.UNDEFINED)
        e2 = les.add(EventType.UNDEFINED)
        assert e1.event_id != e2.event_id

    def test_add_verison_one(self, les):
        e = les.add(EventType.UNDEFINED)
        assert e.metadata.version == 1


class TestGet:
    def test_get_existing(self, les):
        e = les.add(EventType.UNDEFINED)
        assert les.get(e.event_id) is e

    def test_get_nonexistent(self, les):
        assert les.get("nonexistent") is None

    def test_get_after_multiple_adds(self, les):
        e1 = les.add(EventType.UNDEFINED)
        les.add(EventType.UNDEFINED)
        assert les.get(e1.event_id) is e1


class TestUpdate:
    def test_update_new_segment(self, les, seg_100_500, seg_600_900):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        updated = les.update(e.event_id, segment=seg_600_900)
        assert updated.segment is seg_600_900
        assert math.isclose(updated.station_start.value, 600.0)

    def test_update_increments_version(self, les):
        e = les.add(EventType.UNDEFINED)
        updated = les.update(e.event_id)
        assert updated.metadata.version == 2

    def test_update_preserves_event_id(self, les):
        e = les.add(EventType.UNDEFINED)
        updated = les.update(e.event_id)
        assert updated.event_id == e.event_id

    def test_update_new_attributes(self, les):
        e = les.add(EventType.UNDEFINED, attributes={"old": 1})
        updated = les.update(e.event_id, attributes={"new": 2})
        assert updated.attributes["new"] == 2
        assert "old" not in updated.attributes

    def test_update_nonexistent_raises(self, les):
        with pytest.raises(KeyError):
            les.update("nonexistent")

    def test_update_preserves_original(self, les):
        e = les.add(EventType.UNDEFINED, attributes={"k": "v"})
        les.update(e.event_id, attributes={"k": "v2"})
        original = les.get_version(e.event_id, 1)
        assert original is not None
        assert original.attributes["k"] == "v"

    def test_get_version(self, les):
        e = les.add(EventType.UNDEFINED)
        updated = les.update(e.event_id)
        assert les.get_version(e.event_id, 1) is e
        assert les.get_version(e.event_id, 2) is updated
        assert les.get_version(e.event_id, 99) is None


class TestRemove:
    def test_remove_reduces_count(self, les):
        e = les.add(EventType.UNDEFINED)
        les.remove(e.event_id)
        assert les.count == 0

    def test_remove_get_returns_none(self, les):
        e = les.add(EventType.UNDEFINED)
        les.remove(e.event_id)
        assert les.get(e.event_id) is None

    def test_remove_nonexistent_raises(self, les):
        with pytest.raises(KeyError):
            les.remove("nonexistent")

    def test_remove_preserves_other_events(self, les):
        e1 = les.add(EventType.UNDEFINED)
        e2 = les.add(EventType.UNDEFINED)
        les.remove(e1.event_id)
        assert les.count == 1
        assert les.get(e2.event_id) is e2

    def test_remove_audit_trail_preserved(self, les):
        e = les.add(EventType.UNDEFINED)
        les.update(e.event_id)
        les.remove(e.event_id)
        trail = les.audit_trail(e.event_id)
        assert len(trail) == 2


class TestFilter:
    def test_filter_by_type(self, les):
        les.add(EventType.UNDEFINED)
        filtered = les.filter(event_type=EventType.UNDEFINED)
        assert filtered.count == 1

    def test_filter_by_type_empty(self, les):
        filtered = les.filter(event_type=EventType.UNDEFINED)
        assert filtered.count == 0

    def test_filter_default_status(self, les):
        e = les.add(EventType.UNDEFINED)
        filtered = les.filter(event_type=e.event_type)
        assert e.event_id in [ev.event_id for ev in filtered.events]

    def test_filter_returns_new_set(self, les):
        les.add(EventType.UNDEFINED)
        filtered = les.filter()
        assert filtered is not les
        assert filtered.count == les.count

    def test_filter_preserves_axis(self, les):
        filtered = les.filter()
        assert filtered.axis is les.axis

    def test_filter_multiple_types(self, les):
        les.add(EventType.UNDEFINED)
        les.add(EventType.UNDEFINED)
        filtered = les.filter(event_type=EventType.UNDEFINED)
        assert filtered.count == 2


class TestSort:
    def test_sort_by_pk_start(self, les, seg_100_500, seg_600_900):
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        sorted_les = les.sort(by="pk_start")
        events = sorted_les.events
        assert events[0].station_start.value < events[1].station_start.value

    def test_sort_by_length(self, les):
        axis = les.axis
        les.add(EventType.UNDEFINED, segment=Segment(
            _axis=axis, _start=Station(0), _end=Station(200),
            _geometry=Polyline.from_xy([(0, 0), (100, 0), (200, 0)]),
        ))
        les.add(EventType.UNDEFINED, segment=Segment(
            _axis=axis, _start=Station(300), _end=Station(900),
            _geometry=Polyline.from_xy([(300, 0), (600, 0), (900, 0)]),
        ))
        sorted_les = les.sort(by="length")
        events = sorted_les.events
        assert events[0].length <= events[1].length

    def test_sort_returns_new_set(self, les):
        les.add(EventType.UNDEFINED)
        sorted_les = les.sort()
        assert sorted_les is not les


class TestQueryRange:
    def test_query_returns_matching(self, les, seg_100_500, seg_600_900):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        result = les.query_range(200.0, 700.0)
        assert len(result) == 2

    def test_query_excludes_non_matching(self, les, seg_100_500, seg_600_900):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        result = les.query_range(950.0, 1000.0)
        assert len(result) == 0

    def test_query_partial_overlap(self, les, seg_100_500):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        result = les.query_range(400.0, 600.0)
        assert len(result) == 1

    def test_query_empty_set(self, les):
        result = les.query_range(0.0, 100.0)
        assert result == []


class TestOverlaps:
    def test_overlapping_events(self, les, seg_100_500, seg_600_900):
        e1 = les.add(EventType.UNDEFINED, segment=seg_100_500)
        e2 = les.add(EventType.UNDEFINED, segment=Segment(
            _axis=les.axis, _start=Station(400.0), _end=Station(700.0),
            _geometry=Polyline.from_xy([(400, 0), (550, 0), (700, 0)]),
        ))
        overlapping = les.overlaps(e1.event_id)
        assert e2.event_id in [ev.event_id for ev in overlapping]

    def test_non_overlapping_events(self, les, seg_100_500, seg_600_900):
        e1 = les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        overlapping = les.overlaps(e1.event_id)
        assert len(overlapping) == 0

    def test_overlaps_excludes_self(self, les, seg_100_500):
        e1 = les.add(EventType.UNDEFINED, segment=seg_100_500)
        overlapping = les.overlaps(e1.event_id)
        assert e1.event_id not in [ev.event_id for ev in overlapping]

    def test_overlaps_nonexistent_raises(self, les):
        with pytest.raises(KeyError):
            les.overlaps("nonexistent")

    def test_overlaps_no_segment(self, les):
        e = les.add(EventType.UNDEFINED)
        overlapping = les.overlaps(e.event_id)
        assert overlapping == []


class TestGaps:
    def test_gaps_full_coverage(self, les, seg_100_500, seg_600_900):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        gaps_list = les.gaps(EventType.UNDEFINED)
        assert len(gaps_list) >= 1

    def test_gaps_no_events(self, les):
        gaps_list = les.gaps(EventType.UNDEFINED)
        assert len(gaps_list) == 1
        assert math.isclose(gaps_list[0][0], 0.0)
        assert math.isclose(gaps_list[0][1], les.axis.length)

    def test_gaps_type_filter(self, les, seg_100_500):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        gaps_list = les.gaps(EventType.UNDEFINED)
        assert len(gaps_list) <= 2


class TestMerge:
    def test_merge_two_sets(self, les, seg_100_500):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        other = LinearEventSet(les.axis)
        other.add(EventType.UNDEFINED)
        merged = les.merge(other)
        assert merged.count == 2

    def test_merge_same_axis(self, les):
        other = LinearEventSet(les.axis)
        merged = les.merge(other)
        assert merged.count == 0

    def test_merge_different_axis_raises(self, les):
        other_axis = Axis.from_xy([(0, 0), (100, 0)], name="other")
        other = LinearEventSet(other_axis)
        with pytest.raises(ValueError):
            les.merge(other)

    def test_merge_duplicates(self, les):
        e = les.add(EventType.UNDEFINED)
        other = LinearEventSet(les.axis)
        other.add(EventType.UNDEFINED)
        merged = les.merge(other)
        assert merged.get(e.event_id) is not None

    def test_merge_returns_new_set(self, les):
        other = LinearEventSet(les.axis)
        merged = les.merge(other)
        assert merged is not les
        assert merged is not other


class TestSplit:
    def test_split_creates_two(self, les, seg_100_500):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        left, right = les.split(e.event_id, 300.0)
        assert left.event_id == e.event_id
        assert right.event_id != e.event_id
        assert math.isclose(left.station_end.value, 300.0)
        assert math.isclose(right.station_start.value, 300.0)

    def test_split_increments_count(self, les, seg_100_500):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.split(e.event_id, 300.0)
        assert les.count == 2

    def test_split_outside_range_raises(self, les, seg_100_500):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        with pytest.raises(ValueError):
            les.split(e.event_id, 50.0)

    def test_split_no_segment_raises(self, les):
        e = les.add(EventType.UNDEFINED)
        with pytest.raises(ValueError):
            les.split(e.event_id, 100.0)

    def test_split_nonexistent_raises(self, les):
        with pytest.raises(KeyError):
            les.split("nonexistent", 100.0)

    def test_split_preserves_attributes(self, les, seg_100_500):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500, attributes={"k": "v"})
        left, right = les.split(e.event_id, 300.0)
        assert left.attributes["k"] == "v"
        assert right.attributes["k"] == "v"


class TestGroupBy:
    def test_group_by_single_type(self, les):
        les.add(EventType.UNDEFINED)
        les.add(EventType.UNDEFINED)
        groups = les.group_by()
        assert len(groups) == 1
        assert EventType.UNDEFINED in groups

    def test_group_by_empty(self, les):
        groups = les.group_by()
        assert groups == {}

    def test_group_by_multiple_types(self, les):
        les.add(EventType.UNDEFINED)
        groups = les.group_by()
        assert len(groups[EventType.UNDEFINED]) == 1

    def test_group_by_counts(self, les):
        les.add(EventType.UNDEFINED)
        les.add(EventType.UNDEFINED)
        groups = les.group_by()
        assert len(groups[EventType.UNDEFINED]) == 2


class TestAuditTrail:
    def test_audit_trail_initial(self, les):
        e = les.add(EventType.UNDEFINED)
        trail = les.audit_trail(e.event_id)
        assert len(trail) == 1
        assert trail[0] is e

    def test_audit_trail_after_update(self, les):
        e = les.add(EventType.UNDEFINED)
        les.update(e.event_id)
        trail = les.audit_trail(e.event_id)
        assert len(trail) == 2

    def test_audit_trail_preserves_order(self, les):
        e = les.add(EventType.UNDEFINED)
        les.update(e.event_id)
        les.update(e.event_id)
        trail = les.audit_trail(e.event_id)
        assert trail[0].metadata.version == 1
        assert trail[1].metadata.version == 2
        assert trail[2].metadata.version == 3

    def test_audit_trail_nonexistent(self, les):
        trail = les.audit_trail("nonexistent")
        assert trail == []


class TestStatistics:
    def test_statistics_empty(self, les):
        stats = les.statistics()
        assert stats["total_events"] == 0
        assert stats["total_gap_length"] >= 0

    def test_statistics_with_events(self, les, seg_100_500):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        stats = les.statistics()
        assert stats["total_events"] == 1
        assert stats["axis_length"] > 0

    def test_statistics_by_type(self, les):
        les.add(EventType.UNDEFINED)
        stats = les.statistics()
        assert "UNDEFINED" in stats["by_type"]
        assert stats["by_type"]["UNDEFINED"] == 1

    def test_statistics_coverage(self, les, seg_100_500):
        les.add(EventType.UNDEFINED, segment=seg_100_500)
        stats = les.statistics()
        assert 0 <= stats["coverage_pct"] <= 100


class TestEventsProperty:
    def test_events_list(self, les):
        e = les.add(EventType.UNDEFINED)
        assert list(les.events) == [e]

    def test_events_snapshot(self, les):
        les.add(EventType.UNDEFINED)
        events = les.events
        les.add(EventType.UNDEFINED)
        assert len(events) == 1
        assert len(les.events) == 2

    def test_events_empty(self, les):
        assert les.events == []


class TestEdgeCases:
    def test_large_pk_values(self, axis):
        les = LinearEventSet(axis)
        seg = Segment(
            _axis=axis, _start=Station(0.0), _end=Station(999999.999),
            _geometry=Polyline.from_xy([(0, 0), (500000, 0), (1000000, 0)]),
        )
        e = les.add(EventType.UNDEFINED, segment=seg)
        assert math.isclose(e.station_end.value, 999999.999, rel_tol=1e-6)

    def test_multiple_operations(self, les, seg_100_500, seg_600_900):
        e = les.add(EventType.UNDEFINED, segment=seg_100_500)
        les.add(EventType.UNDEFINED, segment=seg_600_900)
        les.update(e.event_id, attributes={"status": "updated"})
        les.remove(e.event_id)
        assert les.count == 1
        trail = les.audit_trail(e.event_id)
        assert len(trail) == 2

    def test_filter_after_remove(self, les):
        e = les.add(EventType.UNDEFINED)
        les.remove(e.event_id)
        filtered = les.filter()
        assert filtered.count == 0

    def test_merge_with_self(self, les):
        les.add(EventType.UNDEFINED)
        merged = les.merge(les)
        assert merged.count == 1

    def test_add_with_references(self, les):
        from dinpro.domain.linear_referencing.event_reference import EventReference
        ref = EventReference(ref_type="test", ref_id="123", provider="test")
        e = les.add(EventType.UNDEFINED, references=(ref,))
        assert len(e.references) == 1
        assert e.references[0].ref_id == "123"
