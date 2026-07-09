from __future__ import annotations

import math
from dataclasses import dataclass

from dinpro.domain.crs.crs import CRS
from dinpro.domain.geometry.point import Point


@dataclass
class TransformationResult:
    point: Point
    source_crs: CRS
    target_crs: CRS
    success: bool
    error: str | None = None


class Transformer:
    def __init__(self) -> None:
        self._adapter = self._load_adapter()

    @staticmethod
    def _load_adapter() -> _BaseAdapter:
        try:
            from dinpro.domain.adapters.pyproj_adapter import PyprojAdapter
            return PyprojAdapter()
        except ImportError:
            return _FallbackAdapter()

    def transform(self, point: Point, source: CRS, target: CRS) -> TransformationResult:
        try:
            result_point = self._adapter.transform(point, source, target)
            return TransformationResult(
                point=result_point,
                source_crs=source,
                target_crs=target,
                success=True,
            )
        except Exception as e:
            return TransformationResult(
                point=point,
                source_crs=source,
                target_crs=target,
                success=False,
                error=str(e),
            )

    def transform_coords(self, x: float, y: float, z: float,
                         source: CRS, target: CRS) -> TransformationResult:
        return self.transform(Point(x, y, z), source, target)

    def can_transform(self, source: CRS, target: CRS) -> bool:
        return self._adapter.can_transform(source, target)

    @property
    def adapter_name(self) -> str:
        return self._adapter.__class__.__name__


class _BaseAdapter:
    def transform(self, point: Point, source: CRS, target: CRS) -> Point:
        raise NotImplementedError

    def can_transform(self, source: CRS, target: CRS) -> bool:
        return source == target


class _FallbackAdapter(_BaseAdapter):
    def transform(self, point: Point, source: CRS, target: CRS) -> Point:
        if source == target:
            return point
        if source.is_geographic() and target.is_utm():
            return self._geo_to_utm(point, target)
        if source.is_utm() and target.is_geographic():
            return self._utm_to_geo(point, source)
        if source.is_utm() and target.is_utm() and source.same_zone(target):
            return point
        raise ValueError(
            f"Cannot transform from {source.name} to {target.name} "
            f"without pyproj. Install pyproj for full CRS support."
        )

    @staticmethod
    def _geo_to_utm(point: Point, target: CRS) -> Point:
        lat = math.radians(point.x)
        lon = math.radians(point.y)
        zone = target.zone or 30
        central_meridian = math.radians((zone - 1) * 6 - 180 + 3)
        a = 6378137.0
        f = 1.0 / 298.257223563
        k0 = 0.9996
        e = math.sqrt(2 * f - f * f)
        n = f / (2 - f)
        a_val = a / (1 + n) * (1 + n * n / 4 + n * n * n * n / 64)
        t = math.sinh(math.atanh(math.sin(lat)) - e * math.atanh(e * math.sin(lat)))
        xi = math.atan(t / math.cos(lon - central_meridian))
        eta = math.atanh(math.sin(lon - central_meridian) / math.sqrt(1 + t * t))
        easting = k0 * a_val * (eta + sum(
            _betas[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta)
            for j in range(3)
        ))
        northing = k0 * a_val * (xi + sum(
            _betas[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta)
            for j in range(3)
        ))
        easting += 500000.0
        if target.hemisphere == "S":
            northing += 10000000.0
        return Point(easting, northing, point.z)

    @staticmethod
    def _utm_to_geo(point: Point, source: CRS) -> Point:
        easting = point.x - 500000.0
        northing = point.y
        if source.hemisphere == "S":
            northing -= 10000000.0
        zone = source.zone or 30
        central_meridian = math.radians((zone - 1) * 6 - 180 + 3)
        k0 = 0.9996
        a = 6378137.0
        f = 1.0 / 298.257223563
        e = math.sqrt(2 * f - f * f)
        n = f / (2 - f)
        a_val = a / (1 + n) * (1 + n * n / 4 + n * n * n * n / 64)
        xi = northing / (k0 * a_val)
        eta = easting / (k0 * a_val)
        xi1 = xi - sum(
            _deltas[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta)
            for j in range(3)
        )
        eta1 = eta - sum(
            _deltas[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta)
            for j in range(3)
        )
        chi = math.asin(math.sin(xi1) / math.cosh(eta1))
        lon = central_meridian + math.atan(math.sinh(eta1) / math.cos(xi1))
        lat = chi
        for _ in range(5):
            lat = chi + e * math.atanh(e * math.sin(lat))
        return Point(math.degrees(lat), math.degrees(lon), point.z)


_betas = [
    0.0,
    (2.0 / 3.0) * 0.00001,
    (5.0 / 3.0) * 0.00001,
]

_deltas = [
    0.0,
    (1.0 / 2.0) * 0.00001,
    (5.0 / 6.0) * 0.00001,
]
