from __future__ import annotations

import enum


class CRSType(enum.Enum):
    UTM = "utm"
    GEOGRAPHIC = "geographic"
    PROJECTED = "projected"
    CUSTOM = "custom"
