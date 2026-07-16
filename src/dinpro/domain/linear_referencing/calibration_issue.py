from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CalibrationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class CalibrationIssue:
    severity: CalibrationSeverity
    code: str
    message: str
    point_index: int | None = None
