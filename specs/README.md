# Specs — Especificaciones técnicas

Todo el diseño debe estar documentado aquí antes de pasar a implementación.

```
specs/
├── core/           → Arquitectura, API, clases, contratos del Core
│   ├── api/        →   Arquitectura de API, secuencia de arranque
│   ├── classes/    →   Project, Axis, Geometry, Settings, Logger...
│   ├── contracts/  →   Module (clase base para plugins)
│   └── interfaces/ →   Protocolos y tipos
├── sdk/            → SDK para desarrollo de plugins externos
├── use_cases/      → Casos de uso
├── uml/            → Diagramas UML
├── flowcharts/     → Diagramas de flujo
├── database/       → Esquema de base de datos
└── protocols/      → Protocolos de comunicación
```
