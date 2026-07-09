import pytest
from dinpro.domain.crs import CRS, CRSRegistry, CRSType


class TestCRS:
    def test_wgs84(self):
        crs = CRSRegistry.get("WGS84")
        assert crs.epsg == 4326
        assert crs.is_geographic()

    def test_etrs89(self):
        crs = CRSRegistry.get("ETRS89")
        assert crs.epsg == 4258

    def test_utm30(self):
        crs = CRSRegistry.get("ETRS89/UTM30N")
        assert crs.epsg == 25830
        assert crs.zone == 30
        assert crs.is_utm()
        assert crs.is_projected()

    def test_utm29(self):
        crs = CRSRegistry.get("ETRS89/UTM29N")
        assert crs.epsg == 25829

    def test_utm31(self):
        crs = CRSRegistry.get("ETRS89/UTM31N")
        assert crs.epsg == 25831

    def test_list_crs(self):
        lst = CRSRegistry.list_crs()
        assert "WGS84" in lst
        assert "ETRS89/UTM30N" in lst

    def test_exists(self):
        assert CRSRegistry.exists("WGS84")
        assert not CRSRegistry.exists("NONEXISTENT")

    def test_create_custom(self):
        crs = CRSRegistry.create_custom("MY_CRS", epsg=9999, description="Custom")
        assert CRSRegistry.exists("MY_CRS")
        assert crs.epsg == 9999

    def test_same_zone(self):
        utm30 = CRSRegistry.get("ETRS89/UTM30N")
        utm30b = CRSRegistry.get("ETRS89/UTM30N")
        assert utm30.same_zone(utm30b)

    def test_different_zone(self):
        utm29 = CRSRegistry.get("ETRS89/UTM29N")
        utm30 = CRSRegistry.get("ETRS89/UTM30N")
        assert not utm29.same_zone(utm30)

    def test_get_by_epsg(self):
        crs = CRS.get("EPSG:25830")
        assert crs.name == "ETRS89/UTM30N"

    def test_get_nonexistent(self):
        with pytest.raises(KeyError):
            CRS.get("NONEXISTENT")

    def test_repr(self):
        crs = CRSRegistry.get("WGS84")
        r = repr(crs)
        assert "CRS" in r
