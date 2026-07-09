# Contrato Module

Todos los módulos de DINPRO deben heredar de esta clase base. Es el contrato que garantiza que cualquier módulo funciona con el Core.

## Clase base

```python
from abc import ABC, abstractmethod

class Module(ABC):
    """Clase base para todos los módulos de DINPRO."""

    @abstractmethod
    def initialize(self) -> None:
        """Preparar el módulo: cargar configuración, recursos, etc."""
        ...

    @abstractmethod
    def run(self) -> None:
        """Ejecutar la lógica principal del módulo."""
        ...

    @abstractmethod
    def validate(self) -> list[str]:
        """Validar resultados. Retorna lista de errores (vacía si ok)."""
        ...

    @abstractmethod
    def export(self, format: str = "json") -> str:
        """Exportar resultados en el formato solicitado."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Liberar recursos. Se llama siempre, incluso si hubo error."""
        ...
```

## Propiedades que cada módulo DEBE definir

```python
    name: str              # "carreteras"
    version: str           # "0.1.0"
    description: str       # "Análisis de carreteras"
    dependencies: list     # ["core>=0.1.0"]
```

## Ciclo de vida

```
1. initialize()  →  Preparar recursos
2. run()         →  Ejecutar lógica
3. validate()    →  Validar resultados
4. export()      →  Exportar si procede
5. cleanup()     →  Liberar recursos (siempre)
```

## Reglas del contrato

1. El módulo NO puede modificar el Core.
2. El módulo NO puede llamar directamente a otro módulo.
3. El módulo SOLO se comunica a través de `project` (API del Core).
4. El módulo DEBE ser autocontenido (no instalar dependencias globales sin avisar).
5. El módulo DEBE usar `project.logger` para toda salida.
