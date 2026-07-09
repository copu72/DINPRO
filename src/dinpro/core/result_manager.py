import json
from typing import Any


class ResultManager:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def add(self, module: str, key: str, data: Any) -> None:
        if module not in self._data:
            self._data[module] = {}
        self._data[module][key] = data

    def get(self, module: str, key: str, default: Any = None) -> Any:
        return self._data.get(module, {}).get(key, default)

    def get_module(self, module: str) -> dict[str, Any]:
        return dict(self._data.get(module, {}))

    def all(self) -> dict[str, dict[str, Any]]:
        return {m: dict(d) for m, d in self._data.items()}

    def clear(self, module: str | None = None) -> None:
        if module:
            self._data.pop(module, None)
        else:
            self._data.clear()

    def export(self, fmt: str = "json") -> str:
        if fmt == "json":
            return json.dumps(self._data, indent=2, ensure_ascii=False)
        raise ValueError(f"Unsupported export format: {fmt}")

    def import_from(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._data.update(data)

    @property
    def modules(self) -> list[str]:
        return list(self._data.keys())

    @property
    def count(self) -> int:
        return sum(len(v) for v in self._data.values())
