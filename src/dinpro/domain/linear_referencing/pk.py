from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Station:
    kilometers: int
    meters: float

    @property
    def total_meters(self) -> float:
        return self.kilometers * 1000.0 + self.meters

    def to_pk_string(self) -> str:
        return f"PK {self.kilometers}+{int(self.meters):03d}"

    def __repr__(self) -> str:
        return self.to_pk_string()


class PK:
    def __init__(self, value: float) -> None:
        self._value = float(value)

    @classmethod
    def from_string(cls, pk_str: str) -> PK:
        pk_str = pk_str.strip().upper().replace("PK ", "").replace("PK", "")
        if "+" in pk_str:
            parts = pk_str.split("+")
            km = int(parts[0])
            m = float(parts[1])
            return cls(km * 1000.0 + m)
        return cls(float(pk_str))

    @classmethod
    def from_station(cls, station: Station) -> PK:
        return cls(station.total_meters)

    @property
    def value(self) -> float:
        return self._value

    def to_station(self) -> Station:
        km = int(self._value / 1000.0)
        m = self._value - km * 1000.0
        return Station(km, m)

    def to_string(self) -> str:
        return self.to_station().to_pk_string()

    def __add__(self, other: PK | float) -> PK:
        if isinstance(other, PK):
            return PK(self._value + other._value)
        return PK(self._value + float(other))

    def __sub__(self, other: PK | float) -> PK:
        if isinstance(other, PK):
            return PK(self._value - other._value)
        return PK(self._value - float(other))

    def __lt__(self, other: PK) -> bool:
        return self._value < other._value

    def __le__(self, other: PK) -> bool:
        return self._value <= other._value

    def __gt__(self, other: PK) -> bool:
        return self._value > other._value

    def __ge__(self, other: PK) -> bool:
        return self._value >= other._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PK):
            return NotImplemented
        return math.isclose(self._value, other._value)

    def __hash__(self) -> int:
        return hash(round(self._value, 6))

    def __repr__(self) -> str:
        return self.to_string()
