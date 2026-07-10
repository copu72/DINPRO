import math

import pytest

from dinpro.domain.linear_referencing.station import Station
from dinpro.domain.linear_referencing.station_formatter import (
    ClassicFormatter,
    CustomFormatter,
    DecimalFormatter,
    EngineeringFormatter,
)
from dinpro.domain.linear_referencing.station_parser import StationParser


class TestStationCreation:
    def test_from_float(self):
        s = Station(15345.235)
        assert math.isclose(s.value, 15345.235)

    def test_from_int(self):
        s = Station(1000)
        assert math.isclose(s.value, 1000.0)

    def test_from_zero(self):
        s = Station(0)
        assert math.isclose(s.value, 0.0)

    def test_negative(self):
        s = Station(-15345.235)
        assert math.isclose(s.value, -15345.235)

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            Station(float("nan"))

    def test_inf_raises(self):
        with pytest.raises(ValueError):
            Station(float("inf"))


class TestStationKilometer:
    def test_kilometer_positive(self):
        s = Station(15345.235)
        assert s.kilometer == 15

    def test_kilometer_exact(self):
        s = Station(15000)
        assert s.kilometer == 15

    def test_kilometer_zero(self):
        s = Station(500)
        assert s.kilometer == 0

    def test_kilometer_negative(self):
        s = Station(-15345.235)
        assert s.kilometer == 15

    def test_kilometer_just_under(self):
        s = Station(14999.999)
        assert s.kilometer == 14


class TestStationMeter:
    def test_meter_positive(self):
        s = Station(15345.235)
        assert math.isclose(s.meter, 345.235)

    def test_meter_exact(self):
        s = Station(15000)
        assert math.isclose(s.meter, 0.0)

    def test_meter_under_1000(self):
        s = Station(500)
        assert math.isclose(s.meter, 500.0)

    def test_meter_negative(self):
        s = Station(-15345.235)
        assert math.isclose(s.meter, 345.235)


class TestStationParse:
    @pytest.fixture
    def parser(self):
        return StationParser()

    def test_plain_number(self, parser):
        s = parser.parse("15345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_format(self, parser):
        s = parser.parse("15+345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_with_decimals(self, parser):
        s = parser.parse("15+345.20")
        assert math.isclose(s.value, 15345.20)

    def test_pk_with_prefix(self, parser):
        s = parser.parse("PK 15+345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_with_lower_prefix(self, parser):
        s = parser.parse("pk15+345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_with_spaces(self, parser):
        s = parser.parse("15 + 345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_with_dot_prefix(self, parser):
        s = parser.parse("P.K. 15+345")
        assert math.isclose(s.value, 15345.0)

    def test_negative_pk(self, parser):
        s = parser.parse("-15+345")
        assert math.isclose(s.value, -15345.0)

    def test_negative_plain(self, parser):
        s = parser.parse("-15345")
        assert math.isclose(s.value, -15345.0)

    def test_station_class_parse(self):
        s = Station.parse("PK 15+345.20")
        assert math.isclose(s.value, 15345.20)

    def test_empty_raises(self, parser):
        with pytest.raises(ValueError):
            parser.parse("")

    def test_invalid_text_raises(self, parser):
        with pytest.raises(ValueError):
            parser.parse("abc")


class TestStationFormatter:
    @pytest.fixture
    def station(self):
        return Station(15345.235)

    def test_classic_default(self, station):
        f = ClassicFormatter()
        assert f.format(station) == "15+345.24"

    def test_classic_3_decimals(self, station):
        f = ClassicFormatter(decimal_places=3)
        assert f.format(station) == "15+345.235"

    def test_classic_zero_decimals(self):
        f = ClassicFormatter(decimal_places=0)
        assert f.format(Station(15000)) == "15+0"

    def test_decimal_default(self, station):
        f = DecimalFormatter()
        assert f.format(station) == "15345.235"

    def test_decimal_2_places(self, station):
        f = DecimalFormatter(decimal_places=2)
        assert f.format(station) == "15345.24"

    def test_engineering_default(self, station):
        f = EngineeringFormatter()
        assert f.format(station) == "15+345.235"

    def test_custom_with_prefix(self, station):
        f = CustomFormatter(prefix="PK")
        assert f.format(station) == "PK 15+345.24"

    def test_custom_no_prefix(self, station):
        f = CustomFormatter(prefix="")
        assert f.format(station) == "15+345.24"


class TestStationToString:
    @pytest.fixture
    def station(self):
        return Station(15345.235)

    def test_default_to_string(self, station):
        assert station.to_string() == "15+345.24"

    def test_to_string_with_classic(self, station):
        assert station.to_string(ClassicFormatter()) == "15+345.24"

    def test_to_string_with_decimal(self, station):
        assert station.to_string(DecimalFormatter()) == "15345.235"

    def test_to_string_with_engineering(self, station):
        assert station.to_string(EngineeringFormatter()) == "15+345.235"


class TestStationComparisons:
    def test_lt(self):
        assert Station(1000) < Station(2000)

    def test_le(self):
        assert Station(1000) <= Station(1000)
        assert Station(1000) <= Station(2000)

    def test_gt(self):
        assert Station(2000) > Station(1000)

    def test_ge(self):
        assert Station(1000) >= Station(1000)
        assert Station(2000) >= Station(1000)

    def test_eq(self):
        assert Station(15345.235) == Station(15345.235)

    def test_eq_close_tolerance(self):
        assert Station(1.0) == Station(1.0000000001)

    def test_ne(self):
        assert not (Station(1000) == Station(2000))

    def test_lt_not_station(self):
        with pytest.raises(TypeError):
            Station(1000) < 500

    def test_le_not_station(self):
        with pytest.raises(TypeError):
            Station(1000) <= 500

    def test_gt_not_station(self):
        with pytest.raises(TypeError):
            Station(1000) > 500

    def test_ge_not_station(self):
        with pytest.raises(TypeError):
            Station(1000) >= 500

    def test_eq_not_station(self):
        assert Station(1000).__eq__(500) is NotImplemented


class TestStationHash:
    def test_hash_equal(self):
        assert hash(Station(15345.235)) == hash(Station(15345.235))

    def test_hash_different(self):
        assert hash(Station(1000)) != hash(Station(2000))

    def test_hashable_in_set(self):
        s = {Station(1000), Station(2000), Station(1000)}
        assert len(s) == 2


class TestStationRound:
    def test_round_more(self):
        s = Station(15345.2357)
        assert math.isclose(s.round(3).value, 15345.236)

    def test_round_less(self):
        s = Station(15345.235)
        assert math.isclose(s.round(2).value, 15345.24)

    def test_round_zero(self):
        s = Station(15345.999)
        assert math.isclose(s.round(0).value, 15346.0)


class TestStationValid:
    def test_valid(self):
        assert Station(1000).is_valid()

    def test_invalid_nan(self):
        Station._value = float("nan")

    def test_inf_not_created(self):
        with pytest.raises(ValueError):
            Station(float("inf"))


class TestStationArithmetic:
    def test_add(self):
        s = Station(1000) + 500.0
        assert math.isclose(s.value, 1500.0)

    def test_sub(self):
        s = Station(1000) - 500.0
        assert math.isclose(s.value, 500.0)

    def test_neg(self):
        s = -Station(1000)
        assert math.isclose(s.value, -1000.0)

    def test_abs_positive(self):
        s = abs(Station(1000))
        assert math.isclose(s.value, 1000.0)

    def test_abs_negative(self):
        s = abs(Station(-1000))
        assert math.isclose(s.value, 1000.0)


class TestStationStrRepr:
    def test_repr(self):
        assert repr(Station(15345.235)) == "Station(15345.235)"

    def test_str(self):
        s = Station(15345.235)
        assert str(s) == s.to_string()


class TestStationPropertyTests:
    def test_parse_format_roundtrip_classic(self):
        stations = [500.0, 1000.0, 15345.235, 99999.999, 0.0, 1.234]
        parser = StationParser()
        formatter = ClassicFormatter(decimal_places=3)
        for val in stations:
            s = Station(val)
            text = formatter.format(s)
            parsed = parser.parse(text)
            assert math.isclose(parsed.value, val, rel_tol=1e-6), (
                f"Roundtrip failed for {val}: {text} -> {parsed.value}"
            )

    def test_parse_format_roundtrip_decimal(self):
        stations = [500.0, 1000.0, 15345.235, 99999.999, 0.0]
        parser = StationParser()
        formatter = DecimalFormatter()
        for val in stations:
            s = Station(val)
            text = formatter.format(s)
            parsed = parser.parse(text)
            assert math.isclose(parsed.value, val, rel_tol=1e-6)

    def test_equality_reflexive(self):
        s = Station(1000)
        assert s == s

    def test_equality_symmetric(self):
        a = Station(1000)
        b = Station(1000)
        assert a == b and b == a

    def test_inequality_consistent(self):
        a = Station(1000)
        b = Station(2000)
        assert a < b
        assert not b < a
        assert a <= b
        assert not b <= a
        assert b > a
        assert not a > b
        assert b >= a
        assert not a >= b

    def test_hash_consistency(self):
        a = Station(1000)
        b = Station(1000)
        assert hash(a) == hash(b)

    def test_km_meter_consistency(self):
        s = Station(15345.235)
        expected = s.kilometer * 1000.0 + s.meter
        assert math.isclose(abs(s.value), expected)


class TestStationParserConstructor:
    def test_equal_seps_raises(self):
        with pytest.raises(ValueError):
            StationParser(decimal_sep="+", pk_sep="+")

    def test_custom_prefix(self):
        p = StationParser(prefix="KM")
        s = p.parse("KM 15+345")
        assert math.isclose(s.value, 15345.0)

    def test_properties(self):
        p = StationParser(decimal_sep=",", pk_sep="-")
        assert p.decimal_sep == ","
        assert p.pk_sep == "-"

    def test_negative_km(self):
        p = StationParser()
        s = p.parse("-1+500")
        assert math.isclose(s.value, -1500.0)

    def test_plain_float(self):
        p = StationParser()
        s = p.parse("1234.567")
        assert math.isclose(s.value, 1234.567)

    def test_plain_float_negative(self):
        p = StationParser()
        s = p.parse("-1234.567")
        assert math.isclose(s.value, -1234.567)

    def test_empty_after_prefix(self):
        p = StationParser()
        with pytest.raises(ValueError):
            p.parse("PK")


class TestStationParserI18n:
    @pytest.fixture
    def es_parser(self):
        return StationParser(decimal_sep=",", pk_sep="+")

    def test_spanish_decimal(self, es_parser):
        s = es_parser.parse("15+345,20")
        assert math.isclose(s.value, 15345.20)

    def test_spanish_pk_no_decimals(self, es_parser):
        s = es_parser.parse("15+345")
        assert math.isclose(s.value, 15345.0)


class TestStationFormatterI18n:
    def test_classic_spanish(self):
        f = ClassicFormatter(decimal_sep=",")
        assert f.format(Station(15345.20)) == "15+345,20"

    def test_decimal_spanish(self):
        f = DecimalFormatter(decimal_sep=",")
        assert f.format(Station(15345.20)) == "15345,200"


class TestStationParserEdgeCases:
    @pytest.fixture
    def parser(self):
        return StationParser()

    def test_leading_plus(self, parser):
        s = parser.parse("+15+345")
        assert math.isclose(s.value, 15345.0)

    def test_pk_sep_different(self):
        p = StationParser(pk_sep="-")
        s = p.parse("15-345")
        assert math.isclose(s.value, 15345.0)

    def test_meter_only(self, parser):
        s = parser.parse("0+500")
        assert math.isclose(s.value, 500.0)

    def test_trailing_zero(self, parser):
        s = parser.parse("15+345.000")
        assert math.isclose(s.value, 15345.0)

    def test_double_plus_sign(self, parser):
        with pytest.raises(ValueError):
            parser.parse("++345")

    def test_missing_meter(self, parser):
        with pytest.raises(ValueError):
            parser.parse("15+")

    def test_negative_km_in_pk(self, parser):
        s = parser.parse("+-2+500")
        assert math.isclose(s.value, -2500.0)


class TestCustomFormatter:
    def test_custom_all_options(self):
        f = CustomFormatter(
            decimal_places=3,
            pk_sep="-",
            decimal_sep=",",
            prefix="PK",
            min_kilometer_len=3,
        )
        result = f.format(Station(15345.235))
        assert result == "PK 15-345,235"

    def test_custom_defaults(self):
        f = CustomFormatter()
        result = f.format(Station(15345.235))
        assert result == "15+345.24"


class TestStationFormatterEdgeCases:
    def test_classic_exact_kilometer(self):
        f = ClassicFormatter(decimal_places=0)
        assert f.format(Station(15000)) == "15+0"

    def test_classic_zero(self):
        f = ClassicFormatter(decimal_places=2)
        assert f.format(Station(0)) == "0+0.00"

    def test_decimal_negative(self):
        f = DecimalFormatter()
        result = f.format(Station(-15345.235))
        assert result == "-15345.235"

    def test_engineering_negative(self):
        f = EngineeringFormatter()
        result = f.format(Station(-15345.235))
        assert result == "15+345.235"


class TestStationFromClassParse:
    def test_parse_classic(self):
        s = Station.parse("15+345.20")
        assert isinstance(s, Station)
        assert math.isclose(s.value, 15345.20)

    def test_parse_with_custom_parser(self):
        parser = StationParser(decimal_sep=",")
        s = Station.parse("15+345,20", parser=parser)
        assert math.isclose(s.value, 15345.20)
