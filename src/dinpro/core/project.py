from pathlib import Path
from typing import Any

from dinpro.core.axis import Axis
from dinpro.core.errors import ProjectError
from dinpro.core.event_bus import EventBus
from dinpro.core.logger import Logger
from dinpro.core.plugin_manager import PluginManager
from dinpro.core.result_manager import ResultManager
from dinpro.core.settings import Settings
from dinpro.core.version import Version


class Project:
    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path else None
        self._version = Version(0, 1, 0)
        self._logger = Logger()
        self._settings = Settings()
        self._axis = Axis()
        self._results = ResultManager()
        self._plugins = PluginManager(logger=self._logger)
        self._events = EventBus()
        self._metadata: dict[str, Any] = {}
        self._is_open = False

    def start(self) -> None:
        self._logger.initialize(level="INFO")
        self._logger.info("DINPRO Professional", "core")
        self._logger.info(f"Version {self._version}", "core")
        self._logger.info("-" * 20, "core")
        self._logger.info("Core initialized", "core")
        self._logger.info("Logger initialized", "core")

        self._settings.load()
        self._logger.set_level(self._settings.log_level)
        self._logger.info("Configuration loaded", "core")

        available = self._plugins.scan()
        if available:
            self._logger.info(f"Available plugins: {', '.join(available)}", "core")
        self._logger.info("Workspace ready", "core")
        self._logger.info("Waiting modules...", "core")

    def open(self, path: str | Path) -> None:
        self._path = Path(path)
        if not self._path.exists():
            raise ProjectError(f"Project file not found: {path}")
        self._logger.info(f"Project opened: {self._path.name}", "core")
        self._is_open = True
        self._events.publish("project.opened", {"path": str(self._path)})

    def save(self) -> None:
        if not self._path:
            raise ProjectError("No project path set")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._export_metadata()
        self._logger.info(f"Project saved: {self._path.name}", "core")
        self._events.publish("project.saved", {"path": str(self._path)})

    def save_as(self, path: str | Path) -> None:
        self._path = Path(path)
        self.save()

    def close(self) -> None:
        for name in self._plugins.loaded():
            self._plugins.unload(name)
        self._results.clear()
        self._axis.clear()
        self._is_open = False
        self._events.publish("project.closed", None)
        self._logger.info("Project closed", "core")

    def _export_metadata(self) -> None:
        if not self._path:
            return
        data = {
            "version": str(self._version),
            "metadata": self._metadata,
            "axis": {
                "vertex_count": self._axis.vertex_count,
                "length": self._axis.length(),
                "crs": self._axis.crs,
            },
        }
        import json
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def axis(self) -> Axis:
        return self._axis

    @property
    def results(self) -> ResultManager:
        return self._results

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def plugins(self) -> PluginManager:
        return self._plugins

    @property
    def events(self) -> EventBus:
        return self._events

    @property
    def version(self) -> Version:
        return self._version

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def is_open(self) -> bool:
        return self._is_open
