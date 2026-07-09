# Arquitectura de DINPRO

## Estructura del repositorio

```
DINPRO
├── .github/
├── docs/
├── src/
│   ├── core/       → Geometry, Project, Engine, Logger, Config, PK, Buffer
│   ├── plugins/    → municipalities, cadastre, roads, rivers, ...
│   ├── gui/
│   ├── io/
│   ├── services/
│   ├── api/
│   └── sdk/
├── tests/
├── data/
├── tools/
├── resources/
├── examples/
├── scripts/
└── assets/
```

## Regla fundamental

**El Core nunca conoce los módulos.**

```
✅  Core ← Módulo
❌  Módulo → Core
```

El Core es la base estable. Los plugins se conectan al Core, nunca al revés.

## Flujo de trabajo del proyecto

```
FASE 0 → Documentación
FASE 1 → Arquitectura
FASE 2 → Core
FASE 3 → Módulos
FASE 4 → GUI
FASE 5 → Pruebas
FASE 6 → Instalador
```

No se saltan fases. Cada fase completa a la anterior.

## Especificación primero

Nada entra en `src/` sin haber pasado por `docs/` primero. Se diseña, se documenta, se implementa.
