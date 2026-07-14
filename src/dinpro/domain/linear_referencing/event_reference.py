from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EventReference:
    ref_type: str
    ref_id: str
    provider: str
