# Changelog

## [0.1.0] - 2026-07-09

### Added
- Paquete `dinpro` instalable (`src/dinpro/`)
- Core completo: Application, Project, Axis, Geometry, Settings, Logger, PluginManager, ResultManager, EventBus, Version, Errors
- Sistema de logging con consola y archivo rotativo
- Configuración global con persistencia JSON
- Sistema de plugins con clase base Module y PluginManager
- Sistema de eventos (EventBus) para comunicación desacoplada
- Jerarquía completa de excepciones
- Operaciones geométricas fundamentales (distancia, ángulo, azimuth, bounding box, interpolación)
- Clase Axis con cálculo de PK, vértices, interpolación y punto más cercano
- 111 tests unitarios, cobertura del 91 %
- Configuración de ruff, black, isort, mypy, pytest

### Changed
- Reestructuración completa: `src/dinpro/` como paquete raíz
- Documentación actualizada en docs/ y specs/

## [0.0.1] - 2026-07-09

### Added
- Estructura completa del repositorio
- Documentación fundacional: Manifiesto, Visión, Arquitectura, Estándares, Reglas IA, Roadmap
- README profesional, LICENSE, .gitignore, pyproject.toml, requirements.txt
