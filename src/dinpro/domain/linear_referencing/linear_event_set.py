from __future__ import annotations

import copy
import uuid
from typing import TYPE_CHECKING, Any

from dinpro.domain.linear_referencing.event_type import EventSource, EventStatus, EventType

if TYPE_CHECKING:
    from dinpro.domain.axis import Axis
    from dinpro.domain.linear_referencing.linear_event import LinearEvent
    from dinpro.domain.linear_referencing.segment import Segment


class LinearEventSet:
    def __init__(self, axis: Axis) -> None:
        self._axis = axis
        self._events: dict[str, list[LinearEvent]] = {}
        self._active: dict[str, LinearEvent] = {}

    @property
    def axis(self) -> Axis:
        return self._axis

    @property
    def count(self) -> int:
        return len(self._active)

    @property
    def events(self) -> list[LinearEvent]:
        return list(self._active.values())

    def add(
        self,
        event_type: EventType,
        segment: Segment | None = None,
        attributes: dict[str, Any] | None = None,
        source: EventSource = EventSource.MANUAL,
        references: tuple[object, ...] = (),
        **metadata_kw: object,
    ) -> LinearEvent:
        from dinpro.domain.linear_referencing.event_metadata import EventMetadata
        from dinpro.domain.linear_referencing.linear_event import LinearEvent

        meta = EventMetadata(source=source, **metadata_kw)  # type: ignore[arg-type]
        attrs = copy.deepcopy(attributes) if attributes else {}
        event = LinearEvent(
            _event_id=uuid.uuid4().hex[:12],
            _event_type=event_type,
            _axis=self._axis,
            _segment=segment,
            _attributes=attrs,
            _metadata=meta,
            _references=references,
        )
        eid = event.event_id
        self._events.setdefault(eid, []).append(event)
        self._active[eid] = event
        return event

    def update(
        self,
        event_id: str,
        segment: object = None,
        attributes: dict[str, Any] | None = None,
        status: object = None,
        **metadata_kw: object,
    ) -> LinearEvent:
        current = self._active.get(event_id)
        if current is None:
            raise KeyError(f"Event {event_id} not found")

        from dinpro.domain.linear_referencing.linear_event import LinearEvent

        new_meta = current.metadata.with_update(status=status, **metadata_kw)
        new_attrs = (
            copy.deepcopy(attributes)
            if attributes is not None
            else copy.deepcopy(current._attributes)
        )
        new_seg = segment if segment is not None else current._segment
        new_refs = current._references

        event = LinearEvent(
            _event_id=event_id,
            _event_type=current.event_type,
            _axis=self._axis,
            _segment=new_seg,
            _attributes=new_attrs,
            _metadata=new_meta,
            _references=new_refs,
        )
        self._events.setdefault(event_id, []).append(event)
        self._active[event_id] = event
        return event

    def remove(self, event_id: str) -> None:
        current = self._active.get(event_id)
        if current is None:
            raise KeyError(f"Event {event_id} not found")
        self._active.pop(event_id)

    def get(self, event_id: str) -> LinearEvent | None:
        return self._active.get(event_id)

    def get_version(self, event_id: str, version: int) -> LinearEvent | None:
        versions = self._events.get(event_id, [])
        for ev in versions:
            if ev.metadata.version == version:
                return ev
        return None

    def filter(
        self,
        event_type: EventType | None = None,
        status: EventStatus = EventStatus.ACTIVE,
    ) -> LinearEventSet:
        result = LinearEventSet(self._axis)
        for ev in self._active.values():
            if event_type is not None and ev.event_type != event_type:
                continue
            if ev.metadata.status != status:
                continue
            result._add_existing(ev)
        return result

    def sort(self, by: str = "pk_start") -> LinearEventSet:
        result = LinearEventSet(self._axis)
        sorted_events = sorted(
            self._active.values(),
            key=lambda e: self._sort_key(e, by),
        )
        for ev in sorted_events:
            result._add_existing(ev)
        return result

    def merge(self, other: LinearEventSet) -> LinearEventSet:
        if other._axis != self._axis:
            raise ValueError("Cannot merge sets with different axis")
        result = LinearEventSet(self._axis)
        for ev in self._active.values():
            result._add_existing(ev)
        for ev in other._active.values():
            existing = result.get(ev.event_id)
            if existing is None:
                result._add_existing(ev)
        return result

    def split(self, event_id: str, pk_split: float) -> tuple[object, object]:
        from dinpro.domain.linear_referencing.linear_event import LinearEvent
        from dinpro.domain.linear_referencing.station import Station

        current = self._active.get(event_id)
        if current is None:
            raise KeyError(f"Event {event_id} not found")
        seg: object = current._segment
        if seg is None:
            raise ValueError("Cannot split an event without segment")
        seg_obj: Segment = seg  # type: ignore[assignment]
        pk = seg_obj._start.value
        pe = seg_obj._end.value
        if not (pk < pk_split < pe):
            raise ValueError(
                f"Split point {pk_split} outside segment range [{pk}, {pe}]"
            )

        left_seg = seg_obj.clip(Station(pk), Station(pk_split))
        right_seg = seg_obj.clip(Station(pk_split), Station(pe))
        new_id = uuid.uuid4().hex[:12]
        meta_left = current.metadata.with_update(notes="split left")
        meta_right = current.metadata.with_update(notes="split right")

        left = LinearEvent(
            _event_id=event_id,
            _event_type=current.event_type,
            _axis=self._axis,
            _segment=left_seg,
            _attributes=copy.deepcopy(current._attributes),
            _metadata=meta_left,
            _references=current._references,
        )
        right = LinearEvent(
            _event_id=new_id,
            _event_type=current.event_type,
            _axis=self._axis,
            _segment=right_seg,
            _attributes=copy.deepcopy(current._attributes),
            _metadata=meta_right,
            _references=current._references,
        )
        self._events.setdefault(event_id, []).append(left)
        self._events[new_id] = [right]
        self._active[event_id] = left
        self._active[new_id] = right
        return left, right

    def group_by(self) -> dict[EventType, list[LinearEvent]]:
        groups: dict[EventType, list[LinearEvent]] = {}
        for ev in self._active.values():
            groups.setdefault(ev.event_type, []).append(ev)
        return groups

    def query_range(
        self,
        pk_start: float,
        pk_end: float,
    ) -> list[LinearEvent]:
        result = []
        for ev in self._active.values():
            seg: object = ev._segment
            if seg is None:
                continue
            seg_obj: Segment = seg  # type: ignore[assignment]
            es = seg_obj._start.value
            ee = seg_obj._end.value
            if es < pk_end and pk_start < ee:
                result.append(ev)
        return result

    def overlaps(self, event_id: str) -> list[LinearEvent]:
        current = self._active.get(event_id)
        if current is None:
            raise KeyError(f"Event {event_id} not found")
        seg: object = current._segment
        if seg is None:
            return []
        seg_obj: Segment = seg  # type: ignore[assignment]
        cs = seg_obj._start.value
        ce = seg_obj._end.value
        result = []
        for ev in self._active.values():
            if ev.event_id == event_id:
                continue
            eseg: object = ev._segment
            if eseg is None:
                continue
            eseg_obj: Segment = eseg  # type: ignore[assignment]
            es = eseg_obj._start.value
            ee = eseg_obj._end.value
            if cs < ee and es < ce:
                result.append(ev)
        return result

    def gaps(self, event_type: EventType) -> list[tuple[float, float]]:
        relevant = []
        for ev in self._active.values():
            if ev.event_type == event_type and ev._segment is not None:
                seg: object = ev._segment
                seg_obj: Segment = seg  # type: ignore[assignment]
                relevant.append((seg_obj._start.value, seg_obj._end.value))
        if not relevant:
            total = self._axis.length
            return [(0.0, total)]
        intervals = sorted(relevant)
        gaps_list: list[tuple[float, float]] = []
        total = self._axis.length
        current_pos = 0.0
        for start, end in intervals:
            if start > current_pos + 1e-9:
                gaps_list.append((current_pos, start))
            current_pos = max(current_pos, end)
        if current_pos < total - 1e-9:
            gaps_list.append((current_pos, total))
        return gaps_list

    def audit_trail(self, event_id: str) -> list[LinearEvent]:
        return list(self._events.get(event_id, []))

    def statistics(self) -> dict[str, Any]:
        total_events = len(self._active)
        by_type = self.group_by()
        total_gap_length = 0.0
        total_axis_length = self._axis.length
        for et in by_type:
            gl = self.gaps(et)
            for g in gl:
                total_gap_length += g[1] - g[0]
        return {
            "total_events": total_events,
            "by_type": {k.name: len(v) for k, v in by_type.items()},
            "total_gap_length": total_gap_length,
            "axis_length": total_axis_length,
            "coverage_pct": (
                (total_axis_length - total_gap_length) / total_axis_length * 100
            ) if total_axis_length > 0 else 0.0,
        }

    def _add_existing(self, event: LinearEvent) -> None:
        eid = event.event_id
        self._events.setdefault(eid, []).append(event)
        self._active[eid] = event

    @staticmethod
    def _sort_key(event: LinearEvent, by: str) -> float:
        seg: object = event._segment
        if by == "pk_start":
            if seg is not None:
                seg_obj: Segment = seg  # type: ignore[assignment]
                return seg_obj._start.value
            return 0.0
        elif by == "pk_end":
            if seg is not None:
                seg_obj = seg  # type: ignore[assignment]
                return seg_obj._end.value
            return 0.0
        elif by == "length":
            return event.length
        elif by == "event_type":
            return hash(event.event_type.value)
        return 0.0

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        return f"LinearEventSet(axis={self._axis}, events={self.count})"
