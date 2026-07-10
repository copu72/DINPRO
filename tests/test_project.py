import json
from pathlib import Path

import pytest

from dinpro.core.errors import ProjectError
from dinpro.core.project import Project


class TestProject:
    def setup_method(self):
        Logger._instance = None
        self.project = Project()

    def test_initial_state(self):
        assert self.project.version is not None
        assert self.project.settings is not None
        assert self.project.logger is not None
        assert self.project.axis is not None
        assert self.project.results is not None
        assert self.project.plugins is not None
        assert self.project.events is not None
        assert self.project.path is None
        assert not self.project.is_open

    def test_start(self):
        self.project.start()
        assert self.project.settings is not None

    def test_save_without_path(self):
        with pytest.raises(ProjectError):
            self.project.save()

    def test_save_and_open(self, tmp_path: Path):
        project_file = tmp_path / "test.dinpro"
        project = Project(project_file)
        project.start()
        project.axis.load([(0, 0), (100, 0)])
        project.save()
        assert project_file.exists()

    def test_close(self):
        self.project.start()
        self.project.axis.load([(0, 0), (10, 0)])
        self.project.close()
        assert not self.project.is_open

    def test_open_nonexistent(self):
        with pytest.raises(ProjectError):
            self.project.open("/nonexistent/file.dinpro")

    def test_version_string(self):
        assert str(self.project.version) == "0.3.1"

    def test_events_on_save(self, tmp_path: Path):
        received = []

        def handler(event, data):
            received.append(event)

        project_file = tmp_path / "test.dinpro"
        project = Project(project_file)
        project.events.subscribe("project.saved", handler)
        project.start()
        project.save()
        assert "project.saved" in received


from dinpro.core.logger import Logger
