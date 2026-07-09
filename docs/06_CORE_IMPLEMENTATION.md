# Core — Implementación v0.1.0

## Resumen

El Core de DINPRO está implementado como un paquete Python instalable (`dinpro`).  
11 clases fundamentales que forman la base sobre la que se apoyarán todos los módulos futuros.

## Clases implementadas

| Clase | Archivo | Responsabilidad |
|-------|---------|-----------------|
| `Application` | `core/application.py` | Punto de entrada. Singleton. Crea y gestiona proyectos. |
| `Project` | `core/project.py` | Objeto único del programa. Contiene todo el estado. |
| `Axis` | `core/axis.py` | Eje de infraestructura lineal. PK, vértices, interpolación. |
| `Geometry` | `core/geometry.py` | Operaciones espaciales fundamentales (stateless). |
| `Settings` | `core/settings.py` | Configuración global con persistencia JSON. |
| `Logger` | `core/logger.py` | Logging centralizado. Consola + archivo rotativo. |
| `PluginManager` | `core/plugin_manager.py` | Carga, descarga y ejecución de módulos. |
| `ResultManager` | `core/result_manager.py` | Almacenamiento estructurado de resultados. |
| `EventBus` | `core/event_bus.py` | Comunicación desacoplada por eventos. |
| `Version` | `core/version.py` | Versión del programa (SemVer). |
| `Errors` | `core/errors.py` | Jerarquía completa de excepciones. |

## Arquitectura

```
Application (singleton)
    └── Project (objeto único)
            ├── Settings        → Configuración global
            ├── Axis            → Eje de la infraestructura
            ├── Geometry        → Operaciones espaciales
            ├── Logger          → Registro de actividad
            ├── PluginManager   → Gestión de módulos
            ├── ResultManager   → Resultados de módulos
            └── EventBus        → Comunicación por eventos
```

## Dependencias

El Core NO tiene dependencias externas. Solo usa la biblioteca estándar de Python.

## Uso mínimo

```python
from dinpro import Project

project = Project()
project.start()
# Salida:
#   DINPRO Professional
#   Version 0.1.0
#   --------------------
#   Core initialized
#   Logger initialized
#   Configuration loaded
#   Workspace ready
#   Waiting modules...
```

## Tests

- **111 tests** unitarios
- **91 % cobertura** global
- Core modules > 95 % (PluginManager requiere plugins reales en disco para cobertura completa)

## Herramientas configuradas

- `pytest` + `pytest-cov` para tests y cobertura
- `ruff` para linting
- `black` para formateo
- `isort` para orden de imports
- `mypy` (strict mode) para tipado estático
