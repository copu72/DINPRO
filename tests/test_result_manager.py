import json
from pathlib import Path

from dinpro.core.result_manager import ResultManager


class TestResultManager:
    def setup_method(self):
        self.rm = ResultManager()

    def test_add_and_get(self):
        self.rm.add("carreteras", "longitud", 100.5)
        assert self.rm.get("carreteras", "longitud") == 100.5

    def test_get_default(self):
        assert self.rm.get("nonexistent", "key", 42) == 42

    def test_get_module(self):
        self.rm.add("carreteras", "a", 1)
        self.rm.add("carreteras", "b", 2)
        module_data = self.rm.get_module("carreteras")
        assert module_data == {"a": 1, "b": 2}

    def test_all(self):
        self.rm.add("m1", "k1", 1)
        self.rm.add("m2", "k2", 2)
        all_data = self.rm.all()
        assert "m1" in all_data
        assert "m2" in all_data
        assert all_data["m1"]["k1"] == 1

    def test_clear_module(self):
        self.rm.add("m1", "k1", 1)
        self.rm.add("m2", "k2", 2)
        self.rm.clear("m1")
        assert self.rm.get("m1", "k1") is None
        assert self.rm.get("m2", "k2") == 2

    def test_clear_all(self):
        self.rm.add("m1", "k1", 1)
        self.rm.add("m2", "k2", 2)
        self.rm.clear()
        assert self.rm.count == 0

    def test_export_json(self):
        self.rm.add("test", "value", 42)
        exported = self.rm.export("json")
        data = json.loads(exported)
        assert data["test"]["value"] == 42

    def test_import(self, tmp_path: Path):
        data_file = tmp_path / "results.json"
        data_file.write_text('{"m1": {"k1": 99}}', encoding="utf-8")
        self.rm.import_from(str(data_file))
        assert self.rm.get("m1", "k1") == 99

    def test_modules_property(self):
        self.rm.add("m1", "k1", 1)
        self.rm.add("m2", "k2", 2)
        assert sorted(self.rm.modules) == ["m1", "m2"]

    def test_count(self):
        self.rm.add("m1", "k1", 1)
        self.rm.add("m1", "k2", 2)
        self.rm.add("m2", "k3", 3)
        assert self.rm.count == 3
