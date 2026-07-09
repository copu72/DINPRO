import json
from pathlib import Path
from typing import Any

from dinpro.core.errors import ConfigurationError


class Settings:
    DEFAULTS: dict[str, Any] = {
        "language": "es",
        "units": "metric",
        "crs_default": "EPSG:25830",
        "log_level": "INFO",
        "log_file": None,
        "plugins_enabled": [],
        "plugins_path": "plugins",
        "autosave": True,
        "autosave_interval": 300,
        "theme": "light",
        "decimal_places": 3,
    }

    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(self.DEFAULTS)
        self._file_path: Path | None = None

    def load(self, path: str | Path | None = None) -> None:
        if path is None:
            path = self._find_config_file()
        if path is None:
            return
        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            self._data.update(data)
            self._file_path = path
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")

    def save(self, path: str | Path | None = None) -> None:
        path = Path(path) if path else self._file_path
        if path is None:
            path = Path("dinpro.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        self._file_path = path

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def reset(self, key: str) -> None:
        if key in self.DEFAULTS:
            self._data[key] = self.DEFAULTS[key]

    def reset_all(self) -> None:
        self._data = dict(self.DEFAULTS)

    def validate(self) -> list[str]:
        errors: list[str] = []
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self._data.get("log_level", "").upper() not in valid_levels:
            errors.append(f"Invalid log_level: {self._data.get('log_level')}")
        if self._data.get("units") not in ("metric", "imperial"):
            errors.append(f"Invalid units: {self._data.get('units')}")
        return errors

    def as_dict(self) -> dict[str, Any]:
        return dict(self._data)

    @property
    def language(self) -> str:
        return str(self._data.get("language", "es"))

    @property
    def units(self) -> str:
        return str(self._data.get("units", "metric"))

    @property
    def crs_default(self) -> str:
        return str(self._data.get("crs_default", "EPSG:25830"))

    @property
    def log_level(self) -> str:
        return str(self._data.get("log_level", "INFO"))

    @property
    def plugins_enabled(self) -> list[str]:
        return list(self._data.get("plugins_enabled", []))

    def _find_config_file(self) -> Path | None:
        candidates = [
            Path("dinpro.json"),
            Path("dinpro.toml"),
            Path.home() / ".dinpro" / "settings.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None
