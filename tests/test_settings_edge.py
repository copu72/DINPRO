import pytest

from dinpro.core.settings import Settings


class TestSettingsEdge:
    def test_load_nonexistent_file_no_error(self):
        s = Settings()
        s.load()
        assert s.language == "es"

    def test_multiple_saves(self, tmp_path):
        s = Settings()
        path = tmp_path / "test.json"
        s.set("language", "en")
        s.save(str(path))
        s.save(str(path))

    def test_set_invalid_key(self):
        s = Settings()
        s.set("custom_key", 123)
        assert s.get("custom_key") == 123

    def test_plugins_enabled_empty_default(self):
        s = Settings()
        assert s.plugins_enabled == []

    def test_settings_units_property(self):
        s = Settings()
        assert s.units == "metric"
        s.set("units", "imperial")
        assert s.units == "imperial"
