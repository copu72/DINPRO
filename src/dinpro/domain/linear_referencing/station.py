from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dinpro.domain.linear_referencing.station_formatter import StationFormatter
    from dinpro.domain.linear_referencing.station_parser import StationParser


@dataclass(frozen=True)
class Station:
    _value: float

    def __post_init__(self) -> None:
        if math.isnan(self._value) or math.isinf(self._value):
            raise ValueError(f"Invalid station value: {self._value}")

    @property
    def value(self) -> float:
        return self._value

    @property
    def kilometer(self) -> int:
        return int(math.floor(abs(self._value) / 1000.0))

    @property
    def meter(self) -> float:
        return abs(self._value) - self.kilometer * 1000.0

    @classmethod
    def parse(cls, text: str, parser: StationParser | None = None) -> Station:
        from dinpro.domain.linear_referencing.station_parser import StationParser as _Parser
        p = parser or _Parser()
        return p.parse(text)

    def to_string(self, formatter: StationFormatter | None = None) -> str:
        from dinpro.domain.linear_referencing.station_formatter import (
            ClassicFormatter as _Formatter,
        )
        f = formatter or _Formatter()
        return f.format(self)

    def round(self, decimals: int) -> Station:
        return Station(round(self._value, decimals))

    def is_valid(self) -> bool:
        return not (math.isnan(self._value) or math.isinf(self._value))

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Station):
            return self._value < other._value
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Station):
            return self._value <= other._value
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Station):
            return self._value > other._value
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Station):
            return self._value >= other._value
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Station):
            return math.isclose(self._value, other._value, rel_tol=1e-9)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(round(self._value, 9))

    def __repr__(self) -> str:
        return f"Station({self._value})"

    def __str__(self) -> str:
        return self.to_string()

    def __neg__(self) -> Station:
        return Station(-self._value)

    def __abs__(self) -> Station:
        return Station(abs(self._value))

    def __add__(self, delta: float) -> Station:
        return Station(self._value + delta)

    def __sub__(self, delta: float) -> Station:
        return Station(self._value - delta)
