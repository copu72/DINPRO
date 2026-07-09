from __future__ import annotations

from dinpro.domain.crs.crs import CRS
from dinpro.domain.geometry.point import Point


class PyprojAdapter:
    def __init__(self) -> None:
        import importlib.util
        self._available = importlib.util.find_spec("pyproj") is not None

    @property
    def available(self) -> bool:
        return self._available

    def can_transform(self, source: CRS, target: CRS) -> bool:
        if not self._available:
            return source == target
        return True

    def transform(self, point: Point, source: CRS, target: CRS) -> Point:
        if not self._available:
            if source == target:
                return point
            raise RuntimeError("pyproj not available and CRS are different")
        if source == target:
            return point
        import pyproj
        src_epsg = source.epsg
        tgt_epsg = target.epsg
        if src_epsg and tgt_epsg:
            transformer = pyproj.Transformer.from_crs(
                f"EPSG:{src_epsg}", f"EPSG:{tgt_epsg}", always_xy=True
            )
            x, y = transformer.transform(point.x, point.y)
            return Point(x, y, point.z)
        if source.proj_string and target.proj_string:
            src_crs = pyproj.CRS(source.proj_string)
            tgt_crs = pyproj.CRS(target.proj_string)
            transformer = pyproj.Transformer.from_crs(src_crs, tgt_crs, always_xy=True)
            x, y = transformer.transform(point.x, point.y)
            return Point(x, y, point.z)
        raise ValueError(f"Cannot transform from {source.name} to {target.name}")
