from pathlib import Path

from dinpro.cad.base.cad_adapter import CADAdapter
from dinpro.cad.base.entity import Block, BlockAttribute, Circle, Layer, Line, Polyline, Text
from dinpro.cad.dxf.reader import DXFReader


class DXFAdapter(CADAdapter):
    def __init__(self) -> None:
        super().__init__()
        self._reader: DXFReader | None = None
        self._open = False

    def open(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"DXF file not found: {path}")
        self._reader = DXFReader()
        self._reader.parse(str(path))
        self._file_path = path
        self._open = True

    def close(self) -> None:
        self._reader = None
        self._open = False

    def get_polylines(self, layer: str | None = None) -> list[Polyline]:
        self._ensure_open()
        return self._reader.get_entities("POLYLINE", layer) + self._reader.get_entities("LWPOLYLINE", layer)

    def get_lines(self, layer: str | None = None) -> list[Line]:
        self._ensure_open()
        return self._reader.get_entities("LINE", layer)

    def get_circles(self, layer: str | None = None) -> list[Circle]:
        self._ensure_open()
        return self._reader.get_entities("CIRCLE", layer)

    def get_texts(self, layer: str | None = None) -> list[Text]:
        self._ensure_open()
        result: list[Text] = []
        result.extend(self._reader.get_entities("TEXT", layer))
        result.extend(self._reader.get_entities("MTEXT", layer))
        return result

    def get_blocks(self, name: str | None = None) -> list[Block]:
        self._ensure_open()
        return self._reader.get_blocks(name)

    def get_layers(self) -> list[Layer]:
        self._ensure_open()
        return self._reader.get_layers()

    def _ensure_open(self) -> None:
        if not self._open or self._reader is None:
            raise RuntimeError("DXF file is not open")

    @property
    def is_open(self) -> bool:
        return self._open
