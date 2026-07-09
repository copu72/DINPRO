from dinpro.core.version import Version


class TestVersion:
    def test_default_version(self):
        v = Version()
        assert str(v) == "0.1.0"
        assert v.label == "DINPRO Professional v0.1.0"

    def test_custom_version(self):
        v = Version(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_from_string(self):
        v = Version.from_string("2.0.1")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 1

    def test_from_string_invalid(self):
        import pytest
        with pytest.raises(ValueError):
            Version.from_string("invalid")

    def test_frozen_dataclass(self):
        v = Version(0, 1, 0)
        import dataclasses
        assert dataclasses.is_dataclass(v)
