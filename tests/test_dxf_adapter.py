from pathlib import Path

import pytest

from dinpro.cad.dxf.dxf_adapter import DXFAdapter


class TestDXFAdapter:
    def setup_method(self):
        self.data_dir = Path(__file__).parent / "data"
        self.dxf_path = self.data_dir / "test.dxf"
        self.adapter = DXFAdapter()

    def test_open(self):
        self.adapter.open(self.dxf_path)
        assert self.adapter.is_open
        assert self.adapter.file_path == self.dxf_path

    def test_open_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            self.adapter.open("nonexistent.dxf")

    def test_close(self):
        self.adapter.open(self.dxf_path)
        self.adapter.close()
        assert not self.adapter.is_open

    def test_get_lines(self):
        self.adapter.open(self.dxf_path)
        lines = self.adapter.get_lines()
        assert len(lines) >= 1
        assert lines[0].length == 100.0

    def test_get_polylines(self):
        self.adapter.open(self.dxf_path)
        polylines = self.adapter.get_polylines()
        assert len(polylines) >= 1
        pl = polylines[0]
        assert len(pl.vertices) >= 2
        assert pl.layer == "AXIS"

    def test_get_polylines_by_layer(self):
        self.adapter.open(self.dxf_path)
        polylines = self.adapter.get_polylines(layer="AXIS")
        assert len(polylines) == 1
        polylines = self.adapter.get_polylines(layer="NONEXISTENT")
        assert len(polylines) == 0

    def test_get_circles(self):
        self.adapter.open(self.dxf_path)
        circles = self.adapter.get_circles()
        assert len(circles) >= 1
        assert circles[0].radius == 25.0

    def test_get_texts(self):
        self.adapter.open(self.dxf_path)
        texts = self.adapter.get_texts()
        assert len(texts) >= 2
        contents = [t.content for t in texts]
        assert "INICIO" in contents
        assert "EJE PRINCIPAL" in contents

    def test_get_layers(self):
        self.adapter.open(self.dxf_path)
        layers = self.adapter.get_layers()
        names = [l.name for l in layers]
        assert "0" in names
        assert "AXIS" in names

    def test_select_all(self):
        self.adapter.open(self.dxf_path)
        sel = self.adapter.select_all()
        assert sel.count >= 3
        assert sel.first_polyline is not None

    def test_select_polyline(self):
        self.adapter.open(self.dxf_path)
        pl = self.adapter.select_polyline()
        assert pl is not None

    def test_operation_on_closed_adapter(self):
        self.adapter.open(self.dxf_path)
        self.adapter.close()
        with pytest.raises(RuntimeError):
            self.adapter.get_lines()

    def test_polyline_length_from_dxf(self):
        self.adapter.open(self.dxf_path)
        pl = self.adapter.get_polylines()[0]
        expected = ((100 ** 2 + 50 ** 2) ** 0.5) * 3
        assert pl.length > 0
