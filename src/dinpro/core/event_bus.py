import uuid
from collections import defaultdict
from collections.abc import Callable
from typing import Any

EventHandler = Callable[[str, dict[str, Any] | None], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, dict[str, EventHandler]] = defaultdict(dict)

    def publish(self, event: str, data: dict[str, Any] | None = None) -> None:
        for subscription_id, handler in list(self._subscribers.get(event, {}).items()):
            try:
                handler(event, data)
            except Exception:
                pass

    def subscribe(self, event: str, handler: EventHandler) -> str:
        subscription_id = str(uuid.uuid4())
        self._subscribers[event][subscription_id] = handler
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        for event in list(self._subscribers.keys()):
            if subscription_id in self._subscribers[event]:
                del self._subscribers[event][subscription_id]
                if not self._subscribers[event]:
                    del self._subscribers[event]
                return

    def clear(self) -> None:
        self._subscribers.clear()

    @property
    def subscribers_count(self) -> int:
        return sum(len(handlers) for handlers in self._subscribers.values())


# System event names
EVENT_PROJECT_OPENED = "project.opened"
EVENT_PROJECT_SAVED = "project.saved"
EVENT_PROJECT_CLOSED = "project.closed"
EVENT_MODULE_LOADED = "module.loaded"
EVENT_MODULE_UNLOADED = "module.unloaded"
EVENT_MODULE_RUN_COMPLETED = "module.run.completed"
EVENT_ERROR = "system.error"
