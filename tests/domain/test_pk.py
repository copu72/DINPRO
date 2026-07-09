import pytest
from dinpro.domain.linear_referencing.pk import PK, Station


class TestPK:
    def test_creation(self):
        pk = PK(25350.0)
        assert pk.value == 25350.0

    def test_from_string(self):
        pk = PK.from_string("PK 25+350")
        assert pk.value == 25350.0

    def test_from_string_no_prefix(self):
        pk = PK.from_string("25+350")
        assert pk.value == 25350.0

    def test_from_float_string(self):
        pk = PK.from_string("1000.5")
        assert pk.value == 1000.5

    def test_to_station(self):
        pk = PK(25350.0)
        s = pk.to_station()
        assert s.kilometers == 25
        assert s.meters == 350.0

    def test_to_string(self):
        pk = PK(25350.0)
        assert pk.to_string() == "PK 25+350"

    def test_repr(self):
        pk = PK(25350.0)
        r = repr(pk)
        assert "PK" in r

    def test_addition(self):
        pk1 = PK(1000)
        pk2 = PK(2000)
        assert (pk1 + pk2).value == 3000.0

    def test_addition_float(self):
        pk = PK(1000)
        assert (pk + 500).value == 1500.0

    def test_subtraction(self):
        pk1 = PK(2000)
        pk2 = PK(1000)
        assert (pk1 - pk2).value == 1000.0

    def test_subtraction_float(self):
        pk = PK(2000)
        assert (pk - 500).value == 1500.0

    def test_less_than(self):
        assert PK(1000) < PK(2000)

    def test_greater_than(self):
        assert PK(2000) > PK(1000)

    def test_equality(self):
        assert PK(1000) == PK(1000)
        assert PK(1000) != PK(2000)

    def test_hash(self):
        s = {PK(1000), PK(1000)}
        assert len(s) == 1

    def test_from_station(self):
        s = Station(25, 350.0)
        pk = PK.from_station(s)
        assert pk.value == 25350.0


class TestStation:
    def test_creation(self):
        s = Station(25, 350.0)
        assert s.kilometers == 25
        assert s.meters == 350.0

    def test_total_meters(self):
        s = Station(25, 350.0)
        assert s.total_meters == 25350.0

    def test_to_pk_string(self):
        s = Station(25, 350)
        assert s.to_pk_string() == "PK 25+350"
