from dataclasses import dataclass, field

from dinpro.cad.base.entity import Block, Circle, Line, Polyline, Text


@dataclass
class Selection:
    polylines: list[Polyline] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    circles: list[Circle] = field(default_factory=list)
    texts: list[Text] = field(default_factory=list)
    blocks: list[Block] = field(default_factory=list)

    @property
    def count(self) -> int:
        return (
            len(self.polylines)
            + len(self.lines)
            + len(self.circles)
            + len(self.texts)
            + len(self.blocks)
        )

    @property
    def first_polyline(self) -> Polyline | None:
        if self.polylines:
            return self.polylines[0]
        return None

    def as_axis_data(self) -> list[tuple[float, float]] | None:
        pl = self.first_polyline
        if pl and len(pl.vertices) >= 2:
            return pl.to_2d()
        if len(self.lines) == 1:
            line = self.lines[0]
            return [(line.start[0], line.start[1]), (line.end[0], line.end[1])]
        return None
