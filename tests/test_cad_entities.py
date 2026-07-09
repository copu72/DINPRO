import math

from dinpro.cad.base.entity import Block, BlockAttribute, Circle, Layer, Line, Polyline, Text


class TestEntityModels:
    def test_line_defaults(self):
        line = Line()
        assert line.layer == "0"
        assert line.start == (0, 0, 0)

    def test_line_with_values(self):
        line = Line(start=(0, 0, 0), end=(10, 0, 0))
        assert line.length == 10.0

    def test_polyline_length_open(self):
        pl = Polyline(vertices=[(0, 0, 0), (10, 0, 0), (10, 10, 0)])
        assert pl.length == 20.0

    def test_polyline_length_closed(self):
        pl = Polyline(vertices=[(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)], closed=True)
        assert math.isclose(pl.length, 40.0)

    def test_polyline_single_vertex(self):
        pl = Polyline(vertices=[(0, 0, 0)])
        assert pl.length == 0.0

    def test_polyline_to_2d(self):
        pl = Polyline(vertices=[(0, 0, 5), (10, 0, 5)])
        assert pl.to_2d() == [(0, 0), (10, 0)]

    def test_circle_length(self):
        c = Circle(radius=10)
        assert math.isclose(c.length, 2 * math.pi * 10)

    def test_text_defaults(self):
        t = Text(content="Hello")
        assert t.height == 2.5
        assert not t.is_mtext

    def test_mtext_flag(self):
        t = Text(content="MText", is_mtext=True)
        assert t.is_mtext

    def test_block_attributes(self):
        attr = BlockAttribute(tag="TAG1", value="123")
        assert attr.tag == "TAG1"
        assert attr.value == "123"

    def test_block(self):
        attr = BlockAttribute(tag="TAG", value="X")
        block = Block(name="SILLA", attributes=[attr])
        assert block.name == "SILLA"
        assert block.attributes[0].value == "X"

    def test_layer(self):
        layer = Layer(name="EJE", color=3, linetype="DASHED")
        assert layer.name == "EJE"
        assert layer.color == 3
        assert layer.linetype == "DASHED"
        assert not layer.locked
