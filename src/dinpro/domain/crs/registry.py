from __future__ import annotations

from dinpro.domain.crs.crs import CRS
from dinpro.domain.crs.types import CRSType

_wgs84 = CRS(
    name="WGS84",
    crs_type=CRSType.GEOGRAPHIC,
    epsg=4326,
    datum="WGS84",
    description="WGS84 Lat/Lon",
)
_wgs84.register()

_etrs89_geo = CRS(
    name="ETRS89",
    crs_type=CRSType.GEOGRAPHIC,
    epsg=4258,
    datum="ETRS89",
    description="ETRS89 Lat/Lon",
)
_etrs89_geo.register()

UTM_ZONES = {
    29: CRS(name="ETRS89/UTM29N", crs_type=CRSType.UTM, epsg=25829, zone=29,
            hemisphere="N", datum="ETRS89", description="ETRS89 UTM zone 29N"),
    30: CRS(name="ETRS89/UTM30N", crs_type=CRSType.UTM, epsg=25830, zone=30,
            hemisphere="N", datum="ETRS89", description="ETRS89 UTM zone 30N"),
    31: CRS(name="ETRS89/UTM31N", crs_type=CRSType.UTM, epsg=25831, zone=31,
            hemisphere="N", datum="ETRS89", description="ETRS89 UTM zone 31N"),
}

for _zone_crs in UTM_ZONES.values():
    _zone_crs.register()


class CRSRegistry:
    @staticmethod
    def get(name: str) -> CRS:
        return CRS.get(name)

    @staticmethod
    def exists(name: str) -> bool:
        return CRS.exists(name)

    @staticmethod
    def list_crs() -> list[str]:
        return CRS.list_registered()

    @staticmethod
    def create_custom(name: str, epsg: int | None = None,
                      proj_string: str | None = None,
                      description: str = "") -> CRS:
        crs = CRS(name=name, crs_type=CRSType.CUSTOM, epsg=epsg,
                  proj_string=proj_string, description=description)
        crs.register()
        return crs
