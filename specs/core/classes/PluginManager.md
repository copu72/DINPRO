# PluginManager

Gestor de módulos/plugins del Core.

## Responsabilidades

- Escanear directorios de plugins.
- Cargar y descargar módulos.
- Verificar que cumplen el contrato Module.
- Ejecutar ciclo de vida de cada módulo.
- Mantener registro de módulos activos.

## API Pública

```python
class PluginManager:
    def scan(self, path: str | None = None) -> list[str]
    def load(self, name: str) -> Module
    def unload(self, name: str) -> None
    def reload(self, name: str) -> Module
    def get(self, name: str) -> Module | None
    def list(self) -> list[str]
    def list_active(self) -> list[str]
    def run_all(self) -> None
    def run(self, name: str) -> None

    @property
    def count(self) -> int
    @property
    def active_count(self) -> int
```

## Detección de módulos

Los plugins se detectan automáticamente si:
1. Están en `src/plugins/<nombre>/`
2. Heredan de `Module`
3. Tienen el archivo `plugin.py` o `__init__.py` con la clase principal
