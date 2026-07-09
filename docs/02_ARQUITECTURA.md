# Arquitectura de DINPRO

## Estructura del repositorio

```
DINPRO
├── .github/       → CI/CD y plantillas
├── docs/          → Documentación del proyecto
├── specs/         → Especificaciones técnicas detalladas
│   ├── core/      →   API, clases, contratos del Core
│   ├── sdk/       →   SDK para plugins externos
│   └── ...
├── src/           → Código fuente
│   ├── core/      →   Project, Axis, Geometry, Logger, Settings...
│   ├── plugins/   →   municipalities, cadastre, roads, rivers...
│   ├── gui/       →   Interfaz de usuario
│   ├── io/        →   Importadores / Exportadores
│   ├── api/       →   API pública
│   └── sdk/       →   SDK para desarrollo de plugins
├── tests/
├── data/
├── tools/         → Herramientas de desarrollo
├── resources/
├── examples/
├── assets/        → Recursos gráficos del proyecto
├── scripts/       → Automatización
└── specs/         → Casos de uso, diagramas, interfaces, contratos
```

## Regla fundamental

**El Core nunca conoce los módulos.**

```
✅  Módulo → Core API → Módulo
❌  Módulo → Módulo (directo)
❌  Core → Módulo
```

Los módulos se comunican exclusivamente a través de la API del Core.

## Flujo de trabajo del proyecto

```
FASE 0  → Documentación      (Sprint 0)
FASE 1  → Arquitectura       (Sprint 0.5)
FASE 2  → Core               (Sprint 1)
FASE 3  → Módulos            (Sprints 2-11)
FASE 4  → GUI                (Sprint 12)
FASE 5  → Pruebas            (transversal)
FASE 6  → Instalador         (final)
```

## Especificación primero

Nada entra en `src/` sin haber pasado por `specs/` primero.
Se diseña la API, se documenta, se implementa.

## Estructura del Core

```
Project
├── Settings
├── Axis
├── Geometry
├── Results
├── Logger
├── PluginManager
├── EventBus
├── Version
├── Workspace
└── ErrorHandler
```

## Diseño para v10.0

Cada decisión de diseño se toma pensando en que DINPRO seguirá activo dentro de 10 años. No se sacrifica arquitectura por rapidez.
