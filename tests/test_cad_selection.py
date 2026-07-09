from dinpro.cad.base.entity import Line, Polyline
from dinpro.cad.base.selection import Selection


class TestSelection:
    def test_empty_selection(self):
        sel = Selection()
        assert sel.count == 0
        assert sel.first_polyline is None
        assert sel.as_axis_data() is None

    def test_selection_with_polyline(self):
        pl = Polyline(vertices=[(0, 0, 0), (100, 0, 0), (100, 100, 0)])
        sel = Selection(polylines=[pl])
        assert sel.count == 1
        assert sel.first_polyline is pl
        axis = sel.as_axis_data()
        assert axis == [(0, 0), (100, 0), (100, 100)]

    def test_selection_with_single_line(self):
        line = Line(start=(0, 0, 0), end=(100, 0, 0))
        sel = Selection(lines=[line])
        axis = sel.as_axis_data()
        assert axis == [(0, 0), (100, 0)]

    def test_selection_multiple_types(self):
        pl = Polyline(vertices=[(0, 0, 0), (10, 0, 0)])
        line = Line(start=(50, 50, 0), end=(100, 100, 0))
        sel = Selection(polylines=[pl], lines=[line])
        assert sel.count == 2
        assert sel.first_polyline is pl
