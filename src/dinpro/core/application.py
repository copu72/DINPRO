from pathlib import Path

from dinpro.core.project import Project
from dinpro.core.version import Version


class Application:
    _instance = None

    def __new__(cls) -> "Application":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._project: Project | None = None
        self._version = Version(0, 3, 1)
        self._initialized = True

    def start(self) -> Project:
        if self._project is None:
            self._project = Project()
            self._project.start()
        return self._project

    def create_project(self, path: str | Path | None = None) -> Project:
        project = Project(path)
        project.start()
        self._project = project
        return project

    def open_project(self, path: str | Path) -> Project:
        project = Project(path)
        project.start()
        project.open(path)
        self._project = project
        return project

    @property
    def project(self) -> Project | None:
        return self._project

    @property
    def version(self) -> Version:
        return self._version
