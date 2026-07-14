import pytest

from dinpro.domain.linear_referencing.event_reference import EventReference


class TestEventReference:
    def test_create(self):
        ref = EventReference(ref_type="municipio", ref_id="sevilla-001", provider="catastro")
        assert ref.ref_type == "municipio"
        assert ref.ref_id == "sevilla-001"
        assert ref.provider == "catastro"

    def test_frozen(self):
        ref = EventReference(ref_type="x", ref_id="y", provider="z")
        with pytest.raises(AttributeError):
            ref.ref_type = "new"

    def test_equality(self):
        r1 = EventReference(ref_type="a", ref_id="1", provider="p")
        r2 = EventReference(ref_type="a", ref_id="1", provider="p")
        assert r1 == r2

    def test_inequality(self):
        r1 = EventReference(ref_type="a", ref_id="1", provider="p")
        r2 = EventReference(ref_type="b", ref_id="1", provider="p")
        assert r1 != r2

    def test_hashable(self):
        s = {EventReference(ref_type="a", ref_id="1", provider="p")}
        assert EventReference(ref_type="a", ref_id="1", provider="p") in s

    def test_repr(self):
        ref = EventReference(ref_type="carretera", ref_id="A-4", provider="dgt")
        r = repr(ref)
        assert "carretera" in r
        assert "A-4" in r
        assert "dgt" in r

    def test_empty_strings_allowed(self):
        ref = EventReference(ref_type="", ref_id="", provider="")
        assert ref.ref_type == ""
        assert ref.ref_id == ""
        assert ref.provider == ""

    def test_any_string_values(self):
        ref = EventReference(ref_type="parcela_123", ref_id="POL-12-PAR-45", provider="catastro")
        assert ref.ref_type == "parcela_123"
