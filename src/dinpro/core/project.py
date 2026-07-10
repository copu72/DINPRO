import json
from pathlib import Path
from typing import Any

from dinpro.cad.factory import open_cad
from dinpro.core.axis import Axis
from dinpro.core.errors import ProjectError
from dinpro.core.event_bus import EventBus
from dinpro.core.logger import Logger
from dinpro.core.plugin_manager import PluginManager
from dinpro.core.result_manager import ResultManager
from dinpro.core.settings import Settings
from dinpro.core.version import Version


class Project:
    PROJECT_EXTENSION = ".din"

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path else None
        self._version = Version(0, 3, 1)
        self._logger = Logger()
        self._settings = Settings()
        self._axis = Axis()
        self._results = ResultManager()
        self._plugins = PluginManager(logger=self._logger)
        self._events = EventBus()
        self._metadata: dict[str, Any] = {}
        self._cad_file: str | None = None
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

        if self._path and self._path.suffix == self.PROJECT_EXTENSION:
            self._load_project_file()
            self._logger.info(f"Project restored: {self._path.name}", "core")

        available = self._plugins.scan()
        if available:
            self._logger.info(f"Available plugins: {', '.join(available)}", "core")
        self._logger.info("Workspace ready", "core")
        self._logger.info("Waiting modules...", "core")

    def open(self, path: str | Path) -> None:
        path = Path(path)
        ext = path.suffix.lower()
        if ext == self.PROJECT_EXTENSION:
            self._path = path
            self._load_project_file()
            self._logger.info(f"Project opened: {path.name}", "core")
        elif ext in (".dwg", ".dxf", ".dws", ".dwt"):
            self._cad_file = str(path)
            self._path = path.with_suffix(self.PROJECT_EXTENSION)
            self._logger.info(f"CAD file linked: {path.name}", "core")
            self._try_load_axis_from_cad()
        else:
            raise ProjectError(f"Unsupported file format: {ext}")
        self._is_open = True
        self._events.publish("project.opened", {"path": str(path)})

    def save(self) -> None:
        if not self._path:
            raise ProjectError("No project path set")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._write_project_file()
        self._logger.info(f"Project saved: {self._path.name}", "core")
        self._events.publish("project.saved", {"path": str(self._path)})

    def save_as(self, path: str | Path) -> None:
        self._path = Path(path)
        if self._path.suffix != self.PROJECT_EXTENSION:
            self._path = self._path.with_suffix(self.PROJECT_EXTENSION)
        self.save()

    def close(self) -> None:
        if self._path and self._is_open:
            self.save()
        for name in self._plugins.loaded():
            self._plugins.unload(name)
        self._results.clear()
        self._axis.clear()
        self._is_open = False
        self._events.publish("project.closed", None)
        self._logger.info("Project closed", "core")

    def load_axis_from_cad(self, path: str | Path | None = None) -> None:
        cad_path = path or self._cad_file
        if not cad_path:
            raise ProjectError("No CAD file specified")
        self._cad_file = str(cad_path)
        self._try_load_axis_from_cad()

    def _try_load_axis_from_cad(self) -> None:
        if not self._cad_file:
            return
        try:
            cad = open_cad(self._cad_file)
            selection = cad.select_all()
            axis_data = selection.as_axis_data()
            if axis_data:
                self._axis.load(axis_data)
                self._logger.info(
                    f"Axis loaded from CAD: {self._axis.length():.2f} m, "
                    f"{self._axis.vertex_count} vertices",
                    "core",
                )
            cad.close()
        except Exception as e:
            self._logger.warning(f"Could not load axis from CAD: {e}", "core")

    def _load_project_file(self) -> None:
        if not self._path or not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            self._metadata = data.get("metadata", {})
            self._cad_file = data.get("cad_file")
            axis_data = data.get("axis", {})
            vertices = axis_data.get("vertices")
            if vertices and len(vertices) >= 2:
                self._axis.load(
                    [(v[0], v[1]) for v in vertices],
                    crs=axis_data.get("crs", "EPSG:25830"),
                )
            results_data = data.get("results", {})
            if results_data:
                for module, module_data in results_data.items():
                    if isinstance(module_data, dict):
                        for key, value in module_data.items():
                            self._results.add(module, key, value)
            settings_data = data.get("settings")
            if settings_data and isinstance(settings_data, dict):
                for key, value in settings_data.items():
                    self._settings.set(key, value)
        except (json.JSONDecodeError, KeyError) as e:
            self._logger.warning(f"Error loading project file: {e}", "core")

    def _write_project_file(self) -> None:
        if not self._path:
            return
        data = {
            "dinpro_version": str(self._version),
            "format_version": "1.0",
            "metadata": self._metadata,
            "cad_file": self._cad_file,
            "settings": self._settings.as_dict(),
            "axis": {
                "vertices": self._axis.vertices(),
                "crs": self._axis.crs,
                "length": self._axis.length(),
                "vertex_count": self._axis.vertex_count,
            },
            "results": self._results.all(),
        }
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

    @property
    def cad_file(self) -> str | None:
        return self._cad_file

    @cad_file.setter
    def cad_file(self, value: str | None) -> None:
        self._cad_file = value
