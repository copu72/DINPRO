from dataclasses import dataclass, field
from typing import Any


@dataclass
class Layer:
    name: str
    color: int = 7
    linetype: str = "Continuous"
    locked: bool = False
    frozen: bool = False
    lineweight: float = 0.25


@dataclass
class Entity:
    handle: str = ""
    layer: str = "0"
    color: int = 7
    linetype: str = "Continuous"
    lineweight: float = 0.25
    visible: bool = True


@dataclass
class Line(Entity):
    start: tuple[float, float, float] = (0.0, 0.0, 0.0)
    end: tuple[float, float, float] = (0.0, 0.0, 0.0)
    length: float = 0.0

    def __post_init__(self) -> None:
        if self.length == 0.0 and (self.start != self.end):
            dx = self.end[0] - self.start[0]
            dy = self.end[1] - self.start[1]
            dz = self.end[2] - self.start[2]
            self.length = (dx * dx + dy * dy + dz * dz) ** 0.5


@dataclass
class Polyline(Entity):
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    closed: bool = False
    elevation: float = 0.0
    width: float = 0.0

    @property
    def length(self) -> float:
        if len(self.vertices) < 2:
            return 0.0
        total = 0.0
        pts = self.vertices if not self.closed else self.vertices + [self.vertices[0]]
        for i in range(len(pts) - 1):
            dx = pts[i + 1][0] - pts[i][0]
            dy = pts[i + 1][1] - pts[i][1]
            total += (dx * dx + dy * dy) ** 0.5
        return total

    def to_2d(self) -> list[tuple[float, float]]:
        return [(v[0], v[1]) for v in self.vertices]


@dataclass
class Circle(Entity):
    center: tuple[float, float, float] = (0.0, 0.0, 0.0)
    radius: float = 0.0

    @property
    def length(self) -> float:
        from math import pi
        return 2 * pi * self.radius


@dataclass
class Text(Entity):
    content: str = ""
    insertion: tuple[float, float, float] = (0.0, 0.0, 0.0)
    height: float = 2.5
    rotation: float = 0.0
    is_mtext: bool = False


@dataclass
class BlockAttribute:
    tag: str = ""
    value: str = ""
    prompt: str = ""


@dataclass
class Block(Entity):
    name: str = ""
    insertion: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: float = 0.0
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    attributes: list[BlockAttribute] = field(default_factory=list)
