from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any

from dinpro.core.errors import PluginError, PluginNotFoundError, PluginLoadError
from dinpro.core.logger import Logger


class Module:
    name: str = ""
    version: str = "0.1.0"
    description: str = ""

    def initialize(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError

    def validate(self) -> list[str]:
        return []

    def export(self, fmt: str = "json") -> str:
        raise NotImplementedError

    def cleanup(self) -> None:
        raise NotImplementedError


class PluginManager:
    def __init__(self, logger: Logger | None = None) -> None:
        self._modules: dict[str, Module] = {}
        self._active: set[str] = set()
        self._paths: list[str] = []
        self._logger = logger

    def scan(self, path: str | Path | None = None) -> list[str]:
        found: list[str] = []
        if path is None:
            paths = self._paths or ["src/dinpro/plugins"]
        else:
            paths = [str(path)]
        for p in paths:
            p_path = Path(p)
            if not p_path.exists():
                continue
            for item in p_path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    found.append(item.name)
        return found

    def load(self, name: str) -> Module:
        if name in self._modules:
            return self._modules[name]
        try:
            module = importlib.import_module(f"dinpro.plugins.{name}")
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Module)
                    and obj is not Module
                ):
                    instance: Module = obj()
                    instance.name = name
                    self._modules[name] = instance
                    self._active.add(name)
                    if self._logger:
                        self._logger.info(f"Plugin loaded: {name}", "core")
                    return instance
            raise PluginLoadError(f"No Module subclass found in plugin: {name}")
        except ImportError as e:
            raise PluginNotFoundError(f"Plugin not found: {name}") from e

    def unload(self, name: str) -> None:
        if name in self._modules:
            self._modules[name].cleanup()
            del self._modules[name]
            self._active.discard(name)
            if self._logger:
                self._logger.info(f"Plugin unloaded: {name}", "core")

    def reload(self, name: str) -> Module:
        self.unload(name)
        module_name = f"dinpro.plugins.{name}"
        if module_name in importlib.import_module("dinpro.plugins").__dict__:
            importlib.reload(importlib.import_module(module_name))
        return self.load(name)

    def get(self, name: str) -> Module | None:
        return self._modules.get(name)

    def loaded(self) -> list[str]:
        return list(self._modules.keys())

    def active(self) -> list[str]:
        return list(self._active)

    def run_all(self) -> None:
        for name in self.loaded():
            self.run(name)

    def run(self, name: str) -> Any:
        if name not in self._modules:
            raise PluginNotFoundError(f"Plugin not loaded: {name}")
        module = self._modules[name]
        if self._logger:
            self._logger.info(f"Running plugin: {name}", "core")
        try:
            module.initialize()
            result = module.run()
            errors = module.validate()
            if errors and self._logger:
                for err in errors:
                    self._logger.warning(f"Validation [{name}]: {err}", "core")
            return result
        except Exception as e:
            if self._logger:
                self._logger.error(f"Plugin error [{name}]: {e}", "core")
            raise PluginError(f"Plugin {name} failed: {e}") from e

    @property
    def count(self) -> int:
        return len(self._modules)

    @property
    def active_count(self) -> int:
        return len(self._active)
