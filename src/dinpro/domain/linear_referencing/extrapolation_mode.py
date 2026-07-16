from __future__ import annotations

from enum import Enum


class ExtrapolationMode(Enum):
    NONE = "none"
    LINEAR = "linear"
    CONSTANT = "constant"
