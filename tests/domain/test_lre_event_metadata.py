import math

import pytest

from dinpro.domain.linear_referencing.event_metadata import EventMetadata
from dinpro.domain.linear_referencing.event_type import EventSource, EventStatus


class TestEventMetadataDefaults:
    def test_default_source(self):
        m = EventMetadata()
        assert m.source == EventSource.MANUAL

    def test_default_status(self):
        m = EventMetadata()
        assert m.status == EventStatus.ACTIVE

    def test_default_version(self):
        m = EventMetadata()
        assert m.version == 1

    def test_default_created_at(self):
        m = EventMetadata()
        assert m.created_at != ""

    def test_default_created_by(self):
        m = EventMetadata()
        assert m.created_by == "system"

    def test_default_confidence(self):
        m = EventMetadata()
        assert m.confidence == 1.0

    def test_default_tags(self):
        m = EventMetadata()
        assert m.tags == ()

    def test_default_notes(self):
        m = EventMetadata()
        assert m.notes == ""

    def test_default_revision(self):
        m = EventMetadata()
        assert m.revision == ""


class TestEventMetadataCustom:
    def test_custom_source(self):
        m = EventMetadata(source=EventSource.API)
        assert m.source == EventSource.API

    def test_custom_status(self):
        m = EventMetadata(status=EventStatus.INACTIVE)
        assert m.status == EventStatus.INACTIVE

    def test_custom_created_by(self):
        m = EventMetadata(created_by="alice")
        assert m.created_by == "alice"

    def test_custom_confidence(self):
        m = EventMetadata(confidence=0.75)
        assert math.isclose(m.confidence, 0.75)

    def test_custom_tags(self):
        m = EventMetadata(tags=("urgent", "review"))
        assert m.tags == ("urgent", "review")

    def test_custom_notes(self):
        m = EventMetadata(notes="test note")
        assert m.notes == "test note"

    def test_custom_version(self):
        m = EventMetadata(version=3)
        assert m.version == 3

    def test_custom_revision(self):
        m = EventMetadata(revision="abc123")
        assert m.revision == "abc123"

    def test_custom_timestamps(self):
        m = EventMetadata(created_at="2026-01-01T00:00:00", updated_at="2026-06-01T00:00:00")
        assert m.created_at == "2026-01-01T00:00:00"
        assert m.updated_at == "2026-06-01T00:00:00"


class TestEventMetadataImmutability:
    def test_frozen(self):
        m = EventMetadata()
        with pytest.raises(AttributeError):
            m.version = 99

    def test_equality(self):
        m1 = EventMetadata(version=1, created_at="x", updated_at="x")
        m2 = EventMetadata(version=1, created_at="x", updated_at="x")
        assert m1 == m2

    def test_inequality(self):
        m1 = EventMetadata(version=1)
        m2 = EventMetadata(version=2)
        assert m1 != m2


class TestEventMetadataWithUpdate:
    def test_version_incremented(self):
        m = EventMetadata()
        updated = m.with_update()
        assert updated.version == 2

    def test_preserves_source(self):
        m = EventMetadata(source=EventSource.API)
        updated = m.with_update()
        assert updated.source == EventSource.API

    def test_updates_timestamp(self):
        m = EventMetadata(updated_at="old")
        updated = m.with_update()
        assert updated.updated_at != "old"

    def test_preserves_created_at(self):
        m = EventMetadata(created_at="original")
        updated = m.with_update()
        assert updated.created_at == "original"

    def test_custom_kwargs(self):
        m = EventMetadata()
        updated = m.with_update(notes="updated note", confidence=0.5)
        assert updated.notes == "updated note"
        assert math.isclose(updated.confidence, 0.5)

    def test_multiple_updates(self):
        m = EventMetadata()
        v2 = m.with_update()
        v3 = v2.with_update()
        assert v3.version == 3
        assert v3.source == EventSource.MANUAL


class TestEventMetadataComputeRevision:
    def test_revision_is_string(self):
        m = EventMetadata()
        rev = m.compute_revision("evt1", 0.0, 100.0)
        assert isinstance(rev, str)

    def test_revision_length(self):
        m = EventMetadata()
        rev = m.compute_revision("evt1", 0.0, 100.0)
        assert len(rev) == 16

    def test_revision_deterministic(self):
        m = EventMetadata()
        rev1 = m.compute_revision("evt1", 0.0, 100.0, {"a": 1})
        rev2 = m.compute_revision("evt1", 0.0, 100.0, {"a": 1})
        assert rev1 == rev2

    def test_revision_changes_with_content(self):
        m = EventMetadata()
        rev1 = m.compute_revision("evt1", 0.0, 100.0)
        rev2 = m.compute_revision("evt1", 0.0, 200.0)
        assert rev1 != rev2

    def test_revision_includes_version(self):
        m1 = EventMetadata(version=1)
        m2 = EventMetadata(version=2)
        rev1 = m1.compute_revision("evt1", 0.0, 100.0)
        rev2 = m2.compute_revision("evt1", 0.0, 100.0)
        assert rev1 != rev2
