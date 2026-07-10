from dinpro.core.version import Version


class TestVersion:
    def test_default_version(self):
        v = Version()
        assert str(v) == "0.3.1"
        assert v.label == "DINPRO Professional v0.3.1"

    def test_custom_version(self):
        v = Version(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_version_with_suffix(self):
        v = Version(0, 3, 1, "-dev")
        assert str(v) == "0.3.1-dev"

    def test_from_string(self):
        v = Version.from_string("2.0.1")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 1

    def test_from_string_with_suffix(self):
        v = Version.from_string("0.3.1-dev")
        assert v.major == 0
        assert v.minor == 3
        assert v.patch == 1
        assert v.suffix == "-dev"

    def test_from_string_invalid(self):
        import pytest
        with pytest.raises(ValueError):
            Version.from_string("invalid")

    def test_frozen_dataclass(self):
        v = Version(0, 3, 1)
        import dataclasses
        assert dataclasses.is_dataclass(v)
