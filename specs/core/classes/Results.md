# Results

Contenedor de resultados generados por los módulos.

## Responsabilidades

- Almacenar resultados de cada módulo por separado.
- Proveer acceso estructurado a los datos.
- Serializar/deserializar resultados.
- Histórico de ejecuciones.

## API Pública

```python
class Results:
    def add(self, module: str, key: str, data: Any) -> None
    def get(self, module: str, key: str, default: Any = None) -> Any
    def get_module(self, module: str) -> dict
    def all(self) -> dict[str, dict]
    def clear(self, module: str | None = None) -> None
    def export(self, format: str = "json") -> str
    def import_from(self, path: str) -> None

    @property
    def modules(self) -> list[str]
    @property
    def count(self) -> int
```

## Ejemplo

```python
project.results.add("carreteras", "longitud_total", 1234.56)
project.results.add("carreteras", "numero_curvas", 12)

longitud = project.results.get("carreteras", "longitud_total")
```
