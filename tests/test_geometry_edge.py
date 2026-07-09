import math

import pytest

from dinpro.core.errors import GeometryError
from dinpro.core.geometry import Geometry


class TestGeometryEdge:
    def test_azimuth_all_directions(self):
        assert pytest.approx(Geometry.azimuth((0, 0), (1, 0))) == 0
        assert pytest.approx(Geometry.azimuth((0, 0), (0, 1))) == 90
        assert pytest.approx(Geometry.azimuth((0, 0), (-1, 0))) == 180
        assert pytest.approx(Geometry.azimuth((0, 0), (0, -1))) == 270

    def test_length_invalid_type(self):
        with pytest.raises(GeometryError):
            Geometry.length("not a geom")

    def test_area_invalid_type(self):
        with pytest.raises(GeometryError):
            Geometry.area("not a geom")

    def test_interpolate_endpoints(self):
        line = [(0, 0), (10, 0)]
        start = Geometry.interpolate(line, 0.0)
        end = Geometry.interpolate(line, 1.0)
        assert start == (0, 0)
        assert end == (10, 0)

    def test_closest_point_zero_length_segment(self):
        result = Geometry.closest_point_on_line((5, 5), (0, 0), (0, 0))
        assert pytest.approx(result[2]) == math.sqrt(50)

    def test_closest_point_middle(self):
        result = Geometry.closest_point_on_line((10, 5), (0, 0), (20, 0))
        assert result[:2] == (10, 0)
        assert pytest.approx(result[2]) == 5.0
