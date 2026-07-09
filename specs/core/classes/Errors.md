# Sistema de Errores

Gestión centralizada de errores del Core.

## Jerarquía de excepciones

```python
class DINPROError(Exception):           # Base de todos los errores
class CoreError(DINPROError):            # Error del Core
class ProjectError(DINPROError):         # Error de proyecto
class AxisError(DINPROError):            # Error de eje
class GeometryError(DINPROError):        # Error geométrico
class SettingsError(DINPROError):        # Error de configuración
class ModuleError(DINPROError):          # Error de módulo
class ModuleNotFoundError(ModuleError)   # Módulo no encontrado
class ModuleLoadError(ModuleError)       # Error al cargar módulo
class ValidationError(DINPROError):      # Error de validación
class ConfigurationError(DINPROError):   # Error de configuración
class IOError(DINPROError):              # Error de entrada/salida
```

## API

```python
class ErrorHandler:
    @staticmethod
    def handle(error: Exception) -> None
    @staticmethod
    def register_handler(error_type: type, handler: Callable) -> None
```

## Uso

```python
try:
    project.axis.load("no_existe.dxf")
except AxisError as e:
    project.logger.error(str(e))
```
