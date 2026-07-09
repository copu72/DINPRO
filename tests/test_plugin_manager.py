import pytest

from dinpro.core.errors import PluginNotFoundError
from dinpro.core.plugin_manager import Module, PluginManager


class TestPluginManager:
    def setup_method(self):
        self.pm = PluginManager()

    def test_initial_state(self):
        assert self.pm.count == 0
        assert self.pm.active_count == 0
        assert self.pm.loaded() == []

    def test_load_nonexistent(self):
        with pytest.raises(PluginNotFoundError):
            self.pm.load("nonexistent_plugin")

    def test_get_nonexistent(self):
        assert self.pm.get("anything") is None

    def test_scan_empty(self):
        found = self.pm.scan("/nonexistent/path")
        assert found == []

    def test_list_active(self):
        assert self.pm.active() == []

    def test_module_base_class(self):
        m = Module()
        with pytest.raises(NotImplementedError):
            m.initialize()
        with pytest.raises(NotImplementedError):
            m.run()
        with pytest.raises(NotImplementedError):
            m.export("json")
        with pytest.raises(NotImplementedError):
            m.cleanup()
        assert m.validate() == []
