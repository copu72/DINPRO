import pytest
from dinpro.domain.transform import Transformer
from dinpro.domain.crs import CRSRegistry
from dinpro.domain.geometry.point import Point


class TestTransformer:
    def test_creation(self):
        t = Transformer()
        assert t is not None

    def test_same_crs(self):
        t = Transformer()
        crs = CRSRegistry.get("ETRS89/UTM30N")
        result = t.transform(Point(500000, 4500000), crs, crs)
        assert result.success
        assert result.point == Point(500000, 4500000)

    def test_can_transform_same(self):
        t = Transformer()
        crs = CRSRegistry.get("ETRS89/UTM30N")
        assert t.can_transform(crs, crs)

    def test_transform_coords(self):
        t = Transformer()
        crs = CRSRegistry.get("ETRS89/UTM30N")
        result = t.transform_coords(500000, 4500000, 0, crs, crs)
        assert result.success

    def test_adapter_name(self):
        t = Transformer()
        assert t.adapter_name in ("PyprojAdapter", "_FallbackAdapter")
