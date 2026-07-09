# Project

El objeto único del programa. TODO vive dentro de Project.

## Responsabilidades

- Abrir, guardar y cerrar proyectos.
- Inicializar el Core completo.
- Exponer todos los subsistemas como propiedades.

## API Pública

```python
class Project:
    def __init__(self, path: str | None = None)
    def start(self) -> None
    def open(self, path: str) -> None
    def save(self) -> None
    def save_as(self, path: str) -> None
    def close(self) -> None

    # Propiedades
    @property
    def settings(self) -> Settings
    @property
    def axis(self) -> Axis
    @property
    def geometry(self) -> Geometry
    @property
    def results(self) -> Results
    @property
    def logger(self) -> Logger
    @property
    def plugins(self) -> PluginManager
    @property
    def events(self) -> EventBus
    @property
    def version(self) -> Version
    @property
    def workspace(self) -> Workspace
```

## Uso esperado

```python
from dinpro import Project

project = Project()
project.start()

# Los módulos acceden al Core a través de project
eje = project.axis.length()
project.logger.info(f"Longitud del eje: {eje}")
```
