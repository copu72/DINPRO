from pathlib import Path

import pytest

from dinpro.core.errors import ProjectError
from dinpro.core.logger import Logger
from dinpro.core.project import Project


class TestProjectEdge:
    def setup_method(self):
        Logger._instance = None

    def test_save_as(self, tmp_path: Path):
        project = Project()
        project.start()
        path = tmp_path / "saved_as"
        project.save_as(str(path))
        assert (tmp_path / "saved_as.din").exists()

    def test_axis_loaded_in_project(self):
        project = Project()
        project.start()
        project.axis.load([(0, 0), (100, 0)])
        assert project.axis.length() == 100.0
        assert project.axis.vertex_count == 2

    def test_results_in_project(self):
        project = Project()
        project.start()
        project.results.add("test", "value", 42)
        assert project.results.get("test", "value") == 42

    def test_events_in_project(self):
        project = Project()
        project.start()
        received = []
        project.events.subscribe("test.event", lambda e, d: received.append(e))
        project.events.publish("test.event")
        assert received == ["test.event"]

    def test_close_with_plugins(self):
        project = Project()
        project.start()
        project.close()

    def test_open_nonexistent_project(self, tmp_path: Path):
        project = Project()
        project.start()
        with pytest.raises(ProjectError):
            project.open(str(tmp_path / "nonexistent.dinpro"))
