import math

import pytest

from dinpro.domain.axis import Axis
from dinpro.domain.geometry.polyline import Polyline
from dinpro.domain.linear_referencing.event_metadata import EventMetadata
from dinpro.domain.linear_referencing.event_reference import EventReference
from dinpro.domain.linear_referencing.event_type import EventSource, EventType
from dinpro.domain.linear_referencing.linear_event import LinearEvent
from dinpro.domain.linear_referencing.segment import Segment
from dinpro.domain.linear_referencing.station import Station


@pytest.fixture
def axis():
    return Axis.from_xy([(0, 0), (500, 0), (1000, 0)], name="test_axis")


@pytest.fixture
def seg(axis):
    return Segment(
        _axis=axis,
        _start=Station(100.0),
        _end=Station(500.0),
        _geometry=Polyline.from_xy([(100, 0), (300, 0), (500, 0)]),
    )


class TestLinearEventCreation:
    def test_create_with_minimal_args(self):
        e = LinearEvent()
        assert e.event_id != ""
        assert e.event_type == EventType.UNDEFINED
        assert e.attributes == {}
        assert e.references == ()

    def test_create_with_segment(self, axis, seg):
        e = LinearEvent(
            _event_type=EventType.UNDEFINED,
            _axis=axis,
            _segment=seg,
            _attributes={"name": "test"},
        )
        assert e.segment is seg
        assert e.station_start == seg.station_start
        assert e.station_end == seg.station_end
        assert e.geometry is seg.geometry
        assert e.length == seg.length

    def test_create_with_references(self, axis):
        ref = EventReference(ref_type="carretera", ref_id="A-4", provider="dgt")
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _references=(ref,))
        assert len(e.references) == 1
        assert e.references[0].ref_id == "A-4"

    def test_invalid_event_type_raises(self, axis):
        with pytest.raises(TypeError):
            LinearEvent(_event_type="not_an_enum", _axis=axis)

    def test_invalid_segment_raises(self, axis):
        with pytest.raises(TypeError):
            LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment="not_a_segment")

    def test_none_segment(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment=None)
        assert e.segment is None
        assert e.geometry is None
        assert e.length == 0.0

    def test_none_segment_station_raises(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment=None)
        with pytest.raises(ValueError):
            _ = e.station_start

    def test_event_id_unique(self):
        e1 = LinearEvent()
        e2 = LinearEvent()
        assert e1.event_id != e2.event_id


class TestLinearEventProperties:
    def test_event_id_stable(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        assert e.event_id == e.event_id

    def test_attributes_copy(self, axis):
        attrs = {"key": "value", "nested": {"a": 1}}
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _attributes=attrs)
        attrs["key"] = "modified"
        assert e.attributes["key"] == "value"

    def test_attributes_independent(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _attributes={"k": "v"})
        attrs = e.attributes
        attrs["k"] = "changed"
        assert e.attributes["k"] == "v"

    def test_metadata_default(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        assert isinstance(e.metadata, EventMetadata)
        assert e.metadata.version == 1

    def test_metadata_custom(self, axis):
        meta = EventMetadata(version=5, source=EventSource.API)
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _metadata=meta)
        assert e.metadata.version == 5
        assert e.metadata.source == EventSource.API

    def test_axis_property(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        assert e.axis is axis


class TestLinearEventImmutability:
    def test_frozen(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        with pytest.raises(AttributeError):
            e._event_id = "new"

    def test_equality(self, axis, seg):
        meta = EventMetadata(version=1, created_at="t", updated_at="t")
        e1 = LinearEvent(
            _event_id="same_id",
            _event_type=EventType.UNDEFINED,
            _axis=axis,
            _segment=seg,
            _attributes={"k": "v"},
            _metadata=meta,
        )
        e2 = LinearEvent(
            _event_id="same_id",
            _event_type=EventType.UNDEFINED,
            _axis=axis,
            _segment=seg,
            _attributes={"k": "v"},
            _metadata=meta,
        )
        assert e1 == e2

    def test_inequality_different_id(self, axis):
        e1 = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        e2 = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        assert e1 != e2

    def test_hashable(self, axis):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis)
        s = {e}
        assert e in s


class TestLinearEventWithSegment:
    def test_station_properties(self, axis, seg):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment=seg)
        assert math.isclose(e.station_start.value, 100.0)
        assert math.isclose(e.station_end.value, 500.0)

    def test_length(self, axis, seg):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment=seg)
        assert e.length > 0

    def test_geometry(self, axis, seg):
        e = LinearEvent(_event_type=EventType.UNDEFINED, _axis=axis, _segment=seg)
        assert e.geometry is seg.geometry
