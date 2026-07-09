from pathlib import Path
from typing import Any

from dinpro.cad.base.cad_adapter import CADAdapter
from dinpro.cad.base.entity import Block, BlockAttribute, Circle, Layer, Line, Polyline, Text


class AutoCADAdapter(CADAdapter):
    def __init__(self) -> None:
        super().__init__()
        self._app: Any = None
        self._doc: Any = None
        self._open = False

    def open(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            import win32com.client
            self._app = win32com.client.Dispatch("AutoCAD.Application")
            self._doc = self._app.Documents.Open(str(path))
            self._app.Visible = False
            self._file_path = path
            self._open = True
        except ImportError:
            raise RuntimeError("pywin32 is required for AutoCAD support")
        except Exception as e:
            raise RuntimeError(f"Failed to open AutoCAD: {e}")

    def close(self) -> None:
        if self._doc:
            try:
                self._doc.Close(False)
            except Exception:
                pass
        self._doc = None
        self._app = None
        self._open = False

    def get_polylines(self, layer: str | None = None) -> list[Polyline]:
        self._ensure_open()
        result: list[Polyline] = []
        for ent in self._iter_entities():
            if ent.EntityName in ("AcDbPolyline", "AcDb2dPolyline", "AcDb3dPolyline"):
                if layer and ent.Layer != layer:
                    continue
                vertices = []
                for i in range(ent.NumberOfVertices):
                    v = ent.Coordinate(i)
                    vertices.append((float(v[0]), float(v[1]), float(v[2]) if hasattr(v, 'z') else 0.0))
                result.append(Polyline(
                    layer=ent.Layer,
                    color=ent.Color,
                    linetype=ent.Linetype,
                    closed=ent.Closed,
                    vertices=vertices,
                    elevation=float(getattr(ent, 'Elevation', 0)),
                ))
        return result

    def get_lines(self, layer: str | None = None) -> list[Line]:
        self._ensure_open()
        result: list[Line] = []
        for ent in self._iter_entities():
            if ent.EntityName == "AcDbLine":
                if layer and ent.Layer != layer:
                    continue
                start = ent.StartPoint
                end = ent.EndPoint
                line = Line(
                    layer=ent.Layer,
                    color=ent.Color,
                    linetype=ent.Linetype,
                    start=(float(start[0]), float(start[1]), float(start[2])),
                    end=(float(end[0]), float(end[1]), float(end[2])),
                )
                line.length = self._dist(line.start, line.end)
                result.append(line)
        return result

    def get_circles(self, layer: str | None = None) -> list[Circle]:
        self._ensure_open()
        result: list[Circle] = []
        for ent in self._iter_entities():
            if ent.EntityName == "AcDbCircle":
                if layer and ent.Layer != layer:
                    continue
                center = ent.Center
                result.append(Circle(
                    layer=ent.Layer,
                    color=ent.Color,
                    center=(float(center[0]), float(center[1]), float(center[2])),
                    radius=float(ent.Radius),
                ))
        return result

    def get_texts(self, layer: str | None = None) -> list[Text]:
        self._ensure_open()
        result: list[Text] = []
        for ent in self._iter_entities():
            if ent.EntityName in ("AcDbText", "AcDbMText"):
                if layer and ent.Layer != layer:
                    continue
                ip = ent.InsertionPoint
                result.append(Text(
                    layer=ent.Layer,
                    color=ent.Color,
                    content=ent.TextString,
                    insertion=(float(ip[0]), float(ip[1]), float(ip[2])),
                    height=float(ent.Height),
                    rotation=float(getattr(ent, 'Rotation', 0)),
                    is_mtext=(ent.EntityName == "AcDbMText"),
                ))
        return result

    def get_blocks(self, name: str | None = None) -> list[Block]:
        self._ensure_open()
        result: list[Block] = []
        for ent in self._iter_entities():
            if ent.EntityName == "AcDbBlockReference":
                if name and ent.Name != name:
                    continue
                ip = ent.InsertionPoint
                atts = []
                try:
                    for attr in ent.GetAttributes():
                        atts.append(BlockAttribute(
                            tag=attr.TagString,
                            value=attr.TextString,
                            prompt=attr.PromptString,
                        ))
                except Exception:
                    pass
                result.append(Block(
                    layer=ent.Layer,
                    name=ent.Name,
                    insertion=(float(ip[0]), float(ip[1]), float(ip[2])),
                    rotation=float(getattr(ent, 'Rotation', 0)),
                    scale=(
                        float(ent.XScaleFactor),
                        float(ent.YScaleFactor),
                        float(ent.ZScaleFactor),
                    ),
                    attributes=atts,
                ))
        return result

    def get_layers(self) -> list[Layer]:
        self._ensure_open()
        result: list[Layer] = []
        for layer in self._doc.Layers:
            result.append(Layer(
                name=layer.Name,
                color=layer.Color,
                linetype=layer.Linetype,
                locked=layer.Lock,
                frozen=layer.Freeze,
            ))
        return result

    def _iter_entities(self):
        if not self._doc:
            return
        try:
            for ent in self._doc.ModelSpace:
                yield ent
        except Exception:
            pass

    def _ensure_open(self) -> None:
        if not self._open:
            raise RuntimeError("AutoCAD document is not open")

    def _dist(self, p1: tuple[float, float, float], p2: tuple[float, float, float]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    @property
    def is_open(self) -> bool:
        return self._open
