from dinpro.core.event_bus import EventBus


class TestEventBusEdge:
    def setup_method(self):
        self.bus = EventBus()

    def test_subscriber_exception_does_not_break(self):
        results = []

        def failing_handler(event, data):
            raise ValueError("oops")

        def good_handler(event, data):
            results.append("ok")

        self.bus.subscribe("test", failing_handler)
        self.bus.subscribe("test", good_handler)
        self.bus.publish("test", None)
        assert results == ["ok"]

    def test_unsubscribe_nonexistent(self):
        self.bus.unsubscribe("nonexistent-id")

    def test_clear_empty(self):
        self.bus.clear()
        assert self.bus.subscribers_count == 0

    def test_publish_no_subscribers(self):
        self.bus.publish("no_subs", {"data": 1})
