from pathlib import Path

from dinpro.core.application import Application


class TestApplication:
    def setup_method(self):
        Application._instance = None

    def test_singleton(self):
        app1 = Application()
        app2 = Application()
        assert app1 is app2

    def test_start(self):
        app = Application()
        project = app.start()
        assert project is not None
        assert app.project is project

    def test_create_project(self):
        app = Application()
        project = app.create_project()
        assert project is not None
        assert project.version is not None

    def test_version(self):
        app = Application()
        assert str(app.version) == "0.3.1"
