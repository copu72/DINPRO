
from dinpro.domain.linear_referencing.event_type import EventSource, EventStatus, EventType


class TestEventType:
    def test_enum_values(self):
        assert EventType.UNDEFINED.value == "undefined"

    def test_equality(self):
        assert EventType.UNDEFINED == EventType.UNDEFINED
        assert EventType.UNDEFINED is EventType.UNDEFINED

    def test_inequality(self):
        assert EventType.UNDEFINED != "undefined"

    def test_hashable(self):
        s = {EventType.UNDEFINED}
        assert EventType.UNDEFINED in s

    def test_iterable(self):
        names = [e.name for e in EventType]
        assert "UNDEFINED" in names


class TestEventSource:
    def test_enum_values(self):
        assert EventSource.MANUAL.value == "manual"
        assert EventSource.SQE.value == "sqe"
        assert EventSource.IMPORT.value == "import"
        assert EventSource.CATALOGO.value == "catalogo"
        assert EventSource.API.value == "api"
        assert EventSource.MIGRATION.value == "migration"

    def test_equality(self):
        assert EventSource.MANUAL == EventSource.MANUAL

    def test_inequality(self):
        assert EventSource.MANUAL != EventSource.SQE

    def test_hashable(self):
        s = {EventSource.MANUAL, EventSource.SQE}
        assert len(s) == 2

    def test_all_sources_defined(self):
        assert len(EventSource) == 6


class TestEventStatus:
    def test_enum_values(self):
        assert EventStatus.ACTIVE.value == "active"
        assert EventStatus.INACTIVE.value == "inactive"
        assert EventStatus.SUPERSEDED.value == "superseded"
        assert EventStatus.DELETED.value == "deleted"

    def test_equality(self):
        assert EventStatus.ACTIVE == EventStatus.ACTIVE

    def test_inequality(self):
        assert EventStatus.ACTIVE != EventStatus.INACTIVE

    def test_hashable(self):
        s = {EventStatus.ACTIVE}
        assert EventStatus.ACTIVE in s

    def test_no_boolean_status(self):
        assert EventStatus.ACTIVE.value != "True"
        assert EventStatus.ACTIVE.value != "False"
        assert EventStatus.INACTIVE.value != "True"
        assert EventStatus.INACTIVE.value != "False"

    def test_all_statuses_defined(self):
        assert len(EventStatus) == 4


class TestEnumUsage:
    def test_event_type_as_type_hint(self):
        def process(et: EventType) -> str:
            return et.value

        assert process(EventType.UNDEFINED) == "undefined"

    def test_event_source_in_function(self):
        def log(src: EventSource) -> str:
            return src.name

        assert log(EventSource.API) == "API"

    def test_event_status_comparison(self):
        active = EventStatus.ACTIVE
        assert active is EventStatus.ACTIVE
        assert active != EventStatus.DELETED
