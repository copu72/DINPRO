from pathlib import Path

import pytest

from dinpro.core.errors import ProjectError
from dinpro.core.logger import Logger
from dinpro.core.project import Project


class TestProjectCAD:
    def setup_method(self):
        Logger._instance = None
        self.data_dir = Path(__file__).parent / "data"

    def test_project_extension(self):
        assert Project.PROJECT_EXTENSION == ".din"

    def test_open_dxf_file(self):
        project = Project()
        project.start()
        project.open(str(self.data_dir / "test.dxf"))
        assert project.is_open
        assert project.cad_file is not None

    def test_save_and_load_din(self, tmp_path: Path):
        din_file = tmp_path / "project.din"
        project = Project(din_file)
        project.start()
        project.axis.load([(0, 0), (100, 0), (200, 0)])
        project.results.add("test", "value", 42)
        project.settings.set("language", "en")
        project.save()
        assert din_file.exists()

        content = din_file.read_text(encoding="utf-8")
        assert "0.2.0" in content
        assert "test" in content

    def test_load_saved_project(self, tmp_path: Path):
        din_file = tmp_path / "project.din"
        project1 = Project(din_file)
        project1.start()
        project1.axis.load([(0, 0), (50, 50), (100, 0)])
        project1.results.add("carreteras", "longitud", 100.5)
        project1.save()

        project2 = Project(din_file)
        project2.start()
        assert project2.axis.vertex_count == 3
        assert project2.results.get("carreteras", "longitud") == 100.5

    def test_save_as(self, tmp_path: Path):
        project = Project()
        project.start()
        project.save_as(str(tmp_path / "myproject.din"))
        assert (tmp_path / "myproject.din").exists()

    def test_save_as_adds_extension(self, tmp_path: Path):
        project = Project()
        project.start()
        project.save_as(str(tmp_path / "myproject"))
        assert (tmp_path / "myproject.din").exists()

    def test_open_unsupported_format(self):
        project = Project()
        project.start()
        with pytest.raises(ProjectError):
            project.open("test.pdf")

    def test_close_auto_saves(self, tmp_path: Path):
        din_file = tmp_path / "autosave.din"
        project = Project()
        project.start()
        project.save_as(str(din_file))
        project.axis.load([(0, 0), (10, 0)])
        project.close()
        assert din_file.exists()

    def test_version_updated(self):
        project = Project()
        assert "0.2.0" in str(project.version)
