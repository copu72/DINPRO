from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dinpro.domain.linear_referencing.station import Station


class StationFormatter(ABC):
    @abstractmethod
    def format(self, station: Station) -> str:
        pass


class ClassicFormatter(StationFormatter):
    def __init__(
        self,
        decimal_places: int = 2,
        pk_sep: str = "+",
        decimal_sep: str = ".",
        min_kilometer_len: int = 2,
    ) -> None:
        self._decimal_places = decimal_places
        self._pk_sep = pk_sep
        self._decimal_sep = decimal_sep
        self._min_kilometer_len = min_kilometer_len

    def format(self, station: Station) -> str:
        km = station.kilometer
        m = station.meter
        meter_str = f"{m:.{self._decimal_places}f}".replace(".", self._decimal_sep)
        return f"{km}{self._pk_sep}{meter_str}"


class DecimalFormatter(StationFormatter):
    def __init__(
        self,
        decimal_places: int = 3,
        decimal_sep: str = ".",
    ) -> None:
        self._decimal_places = decimal_places
        self._decimal_sep = decimal_sep

    def format(self, station: Station) -> str:
        raw = f"{station.value:.{self._decimal_places}f}"
        return raw.replace(".", self._decimal_sep)


class EngineeringFormatter(StationFormatter):
    def __init__(
        self,
        meter_decimal_places: int = 3,
        pk_sep: str = "+",
        decimal_sep: str = ".",
    ) -> None:
        self._meter_decimal_places = meter_decimal_places
        self._pk_sep = pk_sep
        self._decimal_sep = decimal_sep

    def format(self, station: Station) -> str:
        km = station.kilometer
        m = station.meter
        meter_str = f"{m:.{self._meter_decimal_places}f}".replace(".", self._decimal_sep)
        return f"{km}{self._pk_sep}{meter_str}"


class CustomFormatter(StationFormatter):
    def __init__(
        self,
        decimal_places: int = 2,
        pk_sep: str = "+",
        decimal_sep: str = ".",
        prefix: str = "",
        min_kilometer_len: int = 2,
        always_show_sign: bool = False,
    ) -> None:
        self._decimal_places = decimal_places
        self._pk_sep = pk_sep
        self._decimal_sep = decimal_sep
        self._prefix = prefix
        self._min_kilometer_len = min_kilometer_len
        self._always_show_sign = always_show_sign

    def format(self, station: Station) -> str:
        km = station.kilometer
        m = station.meter
        meter_str = f"{m:.{self._decimal_places}f}".replace(".", self._decimal_sep)
        pk_str = f"{km}{self._pk_sep}{meter_str}"
        prefix = f"{self._prefix} " if self._prefix else ""
        return f"{prefix}{pk_str}"
