from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dinpro.domain.linear_referencing.station import Station


@dataclass(frozen=True)
class CalibrationPoint:
    _distance: float
    _station: object
    _source: str = "manual"
    _confidence: float = 1.0

    def __post_init__(self) -> None:
        from dinpro.domain.linear_referencing.station import Station

        if not isinstance(self._station, Station):
            raise TypeError(f"station must be a Station, got {type(self._station)}")
        if not (0.0 <= self._confidence <= 1.0):
            raise ValueError(f"confidence must be in [0, 1], got {self._confidence}")

    @property
    def distance(self) -> float:
        return self._distance

    @property
    def station(self) -> Station:
        return self._station  # type: ignore[return-value]

    @property
    def source(self) -> str:
        return self._source

    @property
    def confidence(self) -> float:
        return self._confidence
