from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class EventMetadata:
    source: object = None
    status: object = None
    version: int = 1
    revision: str = ""
    created_at: str = ""
    created_by: str = "system"
    updated_at: str = ""
    confidence: float = 1.0
    tags: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        from dinpro.domain.linear_referencing.event_type import EventSource, EventStatus

        if self.source is None:
            object.__setattr__(self, "source", EventSource.MANUAL)
        if self.status is None:
            object.__setattr__(self, "status", EventStatus.ACTIVE)
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc).isoformat())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", self.created_at)

    def compute_revision(self, event_id: str, pk_start: float, pk_end: float,
                         attributes: dict[str, object] | None = None,
                         event_type: str = "") -> str:
        raw = f"{event_id}|{pk_start}|{pk_end}|{event_type}|{self.version}|{attributes}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def with_update(self, **kwargs: object) -> EventMetadata:
        now = datetime.now(timezone.utc).isoformat()
        vals: dict[str, object] = {
            "source": self.source,
            "status": self.status,
            "version": self.version + 1,
            "revision": "",
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": now,
            "confidence": self.confidence,
            "tags": self.tags,
            "notes": self.notes,
        }
        vals.update(kwargs)
        vals["version"] = self.version + 1
        return EventMetadata(**vals)  # type: ignore[arg-type]
