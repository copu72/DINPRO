# Logger

Sistema de registro centralizado. Toda salida del programa pasa por aquí. Prohibido usar `print()`.

## Responsabilidades

- Registrar toda la actividad del programa.
- Múltiples niveles de log.
- Salida a consola y archivo simultáneamente.
- Rotación de archivos de log.
- Contexto por módulo.

## API Pública

```python
class Logger:
    def initialize(self, level: str = "INFO", file: str | None = None) -> None
    def debug(self, message: str, module: str | None = None) -> None
    def info(self, message: str, module: str | None = None) -> None
    def warning(self, message: str, module: str | None = None) -> None
    def error(self, message: str, module: str | None = None) -> None
    def critical(self, message: str, module: str | None = None) -> None
    def set_level(self, level: str) -> None

    @property
    def level(self) -> str
    @property
    def file_path(self) -> str | None
```

## Uso

```python
project.logger.info("Eje cargado correctamente", module="carreteras")
project.logger.error("No se pudo abrir el archivo", module="core")
```
