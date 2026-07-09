from pathlib import Path

import pytest

from dinpro.cad.factory import open_cad


class TestCADFactory:
    def setup_method(self):
        self.data_dir = Path(__file__).parent / "data"

    def test_open_dxf(self):
        adapter = open_cad(self.data_dir / "test.dxf")
        assert adapter.is_open
        adapter.close()

    def test_open_nonexistent_dxf(self):
        with pytest.raises(FileNotFoundError):
            open_cad("nonexistent.dxf")

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported CAD file format"):
            open_cad("test.pdf")
