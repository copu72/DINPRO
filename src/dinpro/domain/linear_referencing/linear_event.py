from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dinpro.domain.linear_referencing.event_type import EventType

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.geometry.polyline import Polyline
    from dinpro.domain.linear_referencing.event_metadata import EventMetadata
    from dinpro.domain.linear_referencing.segment import Segment
    from dinpro.domain.linear_referencing.station import Station


@dataclass(frozen=True)
class LinearEvent:
    _event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    _event_type: object = EventType.UNDEFINED
    _axis: object = field(default=None, compare=False)
    _segment: object = field(default=None, compare=False)
    _attributes: dict[str, Any] = field(default_factory=dict, compare=False)
    _metadata: object = field(default=None, compare=False)
    _references: tuple[object, ...] = field(default=(), compare=False)

    def __post_init__(self) -> None:
        from dinpro.domain.linear_referencing.event_metadata import EventMetadata
        from dinpro.domain.linear_referencing.segment import Segment

        if self._metadata is None:
            object.__setattr__(self, "_metadata", EventMetadata())
        if not isinstance(self._event_type, EventType):
            raise TypeError(
                f"event_type must be an EventType, got {type(self._event_type)}"
            )
        if self._segment is not None and not isinstance(self._segment, Segment):
            raise TypeError(
                f"segment must be a Segment, got {type(self._segment)}"
            )
        import copy
        if self._attributes:
            object.__setattr__(self, "_attributes", copy.deepcopy(self._attributes))

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def event_type(self) -> EventType:
        return self._event_type  # type: ignore[return-value]

    @property
    def axis(self) -> Axis:
        return self._axis  # type: ignore[return-value]

    @property
    def segment(self) -> Segment | None:
        return self._segment  # type: ignore[return-value]

    @property
    def station_start(self) -> Station:
        seg: Segment | None = self._segment  # type: ignore[assignment]
        if seg is not None:
            return seg.station_start
        raise ValueError("No segment available")

    @property
    def station_end(self) -> Station:
        seg: Segment | None = self._segment  # type: ignore[assignment]
        if seg is not None:
            return seg.station_end
        raise ValueError("No segment available")

    @property
    def geometry(self) -> Polyline | None:
        seg: Segment | None = self._segment  # type: ignore[assignment]
        if seg is not None:
            return seg.geometry
        return None

    @property
    def length(self) -> float:
        seg: Segment | None = self._segment  # type: ignore[assignment]
        if seg is not None:
            return seg.length
        return 0.0

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self._attributes)

    @property
    def metadata(self) -> EventMetadata:
        return self._metadata  # type: ignore[return-value]

    @property
    def references(self) -> tuple[object, ...]:
        return self._references
