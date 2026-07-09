from abc import ABC, abstractmethod
from pathlib import Path

from dinpro.cad.base.entity import Block, Circle, Layer, Line, Polyline, Text
from dinpro.cad.base.selection import Selection


class CADAdapter(ABC):
    def __init__(self) -> None:
        self._file_path: Path | None = None

    @abstractmethod
    def open(self, path: str | Path) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def get_polylines(self, layer: str | None = None) -> list[Polyline]:
        ...

    @abstractmethod
    def get_lines(self, layer: str | None = None) -> list[Line]:
        ...

    @abstractmethod
    def get_circles(self, layer: str | None = None) -> list[Circle]:
        ...

    @abstractmethod
    def get_texts(self, layer: str | None = None) -> list[Text]:
        ...

    @abstractmethod
    def get_blocks(self, name: str | None = None) -> list[Block]:
        ...

    @abstractmethod
    def get_layers(self) -> list[Layer]:
        ...

    def select_all(self) -> Selection:
        return Selection(
            polylines=self.get_polylines(),
            lines=self.get_lines(),
            circles=self.get_circles(),
            texts=self.get_texts(),
            blocks=self.get_blocks(),
        )

    def select_polyline(self, prompt: str = "Select polyline:") -> Polyline | None:
        polylines = self.get_polylines()
        if len(polylines) == 1:
            return polylines[0]
        return None

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    @property
    @abstractmethod
    def is_open(self) -> bool:
        ...
