import json
from pathlib import Path

from dinpro.core.errors import ConfigurationError
from dinpro.core.settings import Settings


class TestSettings:
    def setup_method(self):
        self.settings = Settings()

    def test_defaults(self):
        assert self.settings.language == "es"
        assert self.settings.units == "metric"
        assert self.settings.crs_default == "EPSG:25830"
        assert self.settings.log_level == "INFO"

    def test_get_set(self):
        self.settings.set("language", "en")
        assert self.settings.get("language") == "en"
        assert self.settings.language == "en"

    def test_get_default(self):
        assert self.settings.get("nonexistent", 42) == 42

    def test_reset(self):
        self.settings.set("language", "en")
        self.settings.reset("language")
        assert self.settings.language == "es"

    def test_reset_all(self):
        self.settings.set("language", "en")
        self.settings.set("units", "imperial")
        self.settings.reset_all()
        assert self.settings.language == "es"
        assert self.settings.units == "metric"

    def test_validate_valid(self):
        errors = self.settings.validate()
        assert errors == []

    def test_validate_invalid_log_level(self):
        self.settings.set("log_level", "invalid")
        errors = self.settings.validate()
        assert len(errors) > 0

    def test_validate_invalid_units(self):
        self.settings.set("units", "invalid")
        errors = self.settings.validate()
        assert len(errors) > 0

    def test_as_dict(self):
        d = self.settings.as_dict()
        assert d["language"] == "es"
        assert d["units"] == "metric"

    def test_save_and_load(self, tmp_path: Path):
        config_file = tmp_path / "dinpro.json"
        self.settings.set("language", "fr")
        self.settings.save(str(config_file))

        new_settings = Settings()
        new_settings.load(str(config_file))
        assert new_settings.language == "fr"
        assert new_settings.units == "metric"

    def test_load_file_not_found(self):
        with self.assert_raises(ConfigurationError):
            self.settings.load("/nonexistent/config.json")

    @staticmethod
    def assert_raises(exc_type):
        import pytest
        return pytest.raises(exc_type)

    def test_plugins_enabled(self):
        assert self.settings.plugins_enabled == []
        self.settings.set("plugins_enabled", ["carreteras", "catastro"])
        assert self.settings.plugins_enabled == ["carreteras", "catastro"]
