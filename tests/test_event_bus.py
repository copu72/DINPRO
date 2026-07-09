from dinpro.core.event_bus import (
    EVENT_PROJECT_OPENED,
    EVENT_PROJECT_SAVED,
    EventBus,
)


class TestEventBus:
    def setup_method(self):
        self.bus = EventBus()

    def test_subscribe_and_publish(self):
        received = []

        def handler(event, data):
            received.append((event, data))

        self.bus.subscribe("test.event", handler)
        self.bus.publish("test.event", {"key": "value"})
        assert len(received) == 1
        assert received[0] == ("test.event", {"key": "value"})

    def test_multiple_subscribers(self):
        results = []

        def handler1(event, data):
            results.append("h1")

        def handler2(event, data):
            results.append("h2")

        self.bus.subscribe("evt", handler1)
        self.bus.subscribe("evt", handler2)
        self.bus.publish("evt", None)
        assert len(results) == 2

    def test_unsubscribe(self):
        received = []

        def handler(event, data):
            received.append(1)

        sid = self.bus.subscribe("test", handler)
        self.bus.publish("test", None)
        assert len(received) == 1
        self.bus.unsubscribe(sid)
        self.bus.publish("test", None)
        assert len(received) == 1

    def test_clear(self):
        self.bus.subscribe("evt", lambda e, d: None)
        self.bus.subscribe("evt2", lambda e, d: None)
        assert self.bus.subscribers_count == 2
        self.bus.clear()
        assert self.bus.subscribers_count == 0

    def test_system_events_exist(self):
        assert EVENT_PROJECT_OPENED == "project.opened"
        assert EVENT_PROJECT_SAVED == "project.saved"
