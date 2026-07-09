import pytest

from dinpro.core.axis import Axis
from dinpro.core.errors import AxisError


class TestAxis:
    def setup_method(self):
        self.axis = Axis()
        self.vertices = [(0, 0), (100, 0), (100, 100), (0, 100)]

    def test_load(self):
        self.axis.load(self.vertices)
        assert self.axis.vertex_count == 4
        assert self.axis.crs == "EPSG:25830"

    def test_load_insufficient_vertices(self):
        with pytest.raises(AxisError):
            self.axis.load([(0, 0)])

    def test_length(self):
        self.axis.load(self.vertices)
        assert self.axis.length() == 300.0

    def test_length_straight_line(self):
        self.axis.load([(0, 0), (10, 0)])
        assert self.axis.length() == 10.0

    def test_vertices(self):
        self.axis.load(self.vertices)
        verts = self.axis.vertices()
        assert verts == self.vertices
        verts.append((999, 999))
        assert len(self.axis.vertices()) == 4

    def test_interpolate(self):
        self.axis.load([(0, 0), (100, 0)])
        point = self.axis.interpolate(0.5)
        assert point == (50.0, 0.0)

    def test_pk(self):
        self.axis.load([(0, 0), (100, 0)])
        pk = self.axis.pk((50, 0))
        assert pytest.approx(pk, 0.01) == 50.0
        pk = self.axis.pk((0, 0))
        assert pytest.approx(pk, 0.01) == 0.0

    def test_point(self):
        self.axis.load([(0, 0), (100, 0)])
        p = self.axis.point(50.0)
        assert p == (50.0, 0.0)

    def test_point_out_of_range(self):
        self.axis.load([(0, 0), (10, 0)])
        with pytest.raises(AxisError):
            self.axis.point(100.0)

    def test_closest_point(self):
        self.axis.load([(0, 0), (10, 0)])
        result = self.axis.closest_point((5, 5))
        assert result[:2] == (5.0, 0.0)
        assert pytest.approx(result[2]) == 5.0

    def test_clear(self):
        self.axis.load(self.vertices)
        self.axis.clear()
        assert self.axis.vertex_count == 0
        assert self.axis.length() == 0.0

    def test_crs_property(self):
        self.axis.load(self.vertices, "EPSG:25830")
        assert self.axis.crs == "EPSG:25830"
        self.axis.crs = "EPSG:4326"
        assert self.axis.crs == "EPSG:4326"
