from __future__ import annotations

from typing import ClassVar

from dinpro.domain.crs.types import CRSType


class CRS:
    _registry: ClassVar[dict[str, CRS]] = {}

    def __init__(self, name: str, crs_type: CRSType, epsg: int | None = None,
                 proj_string: str | None = None, zone: int | None = None,
                 hemisphere: str = "N", datum: str = "ETRS89",
                 description: str = "") -> None:
        self._name = name
        self._type = crs_type
        self._epsg = epsg
        self._proj_string = proj_string
        self._zone = zone
        self._hemisphere = hemisphere
        self._datum = datum
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def crs_type(self) -> CRSType:
        return self._type

    @property
    def epsg(self) -> int | None:
        return self._epsg

    @property
    def proj_string(self) -> str | None:
        return self._proj_string

    @property
    def zone(self) -> int | None:
        return self._zone

    @property
    def hemisphere(self) -> str:
        return self._hemisphere

    @property
    def datum(self) -> str:
        return self._datum

    @property
    def description(self) -> str:
        return self._description

    def is_geographic(self) -> bool:
        return self._type == CRSType.GEOGRAPHIC

    def is_utm(self) -> bool:
        return self._type == CRSType.UTM

    def is_projected(self) -> bool:
        return self._type in (CRSType.UTM, CRSType.PROJECTED)

    def same_zone(self, other: CRS) -> bool:
        return self._zone == other._zone and self._hemisphere == other._hemisphere

    def register(self) -> None:
        CRS._registry[self._name] = self
        if self._epsg:
            CRS._registry[f"EPSG:{self._epsg}"] = self

    @classmethod
    def get(cls, identifier: str) -> CRS:
        if identifier in cls._registry:
            return cls._registry[identifier]
        raise KeyError(f"CRS '{identifier}' not registered")

    @classmethod
    def exists(cls, identifier: str) -> bool:
        return identifier in cls._registry

    @classmethod
    def list_registered(cls) -> list[str]:
        return list(cls._registry.keys())

    def __repr__(self) -> str:
        return f"CRS({self._name}, epsg={self._epsg})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CRS):
            return NotImplemented
        return self._name == other._name

    def __hash__(self) -> int:
        return hash(self._name)
