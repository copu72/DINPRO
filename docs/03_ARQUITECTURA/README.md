# Arquitectura DINPRO v1.0

## REGLA Nº1 — Estructura inmutable

Esta estructura NO se cambiará sin revisión de arquitectura.

```
DINPRO
├── .github/
├── docs/
├── specs/       → Especificaciones (use cases, UML, DB, interfaces)
├── src/
│   ├── core/    → Geometry, Project, Engine, Logger, Config, PK, Buffer
│   ├── plugins/ → municipalities, cadastre, roads, rivers, ...
│   ├── gui/     → windows, dialogs, widgets, themes
│   ├── io/      → importers, exporters, converters
│   ├── services/
│   ├── api/
│   └── sdk/     → Public API para desarrollo de plugins externos
├── tests/
├── data/
├── resources/
├── examples/
├── assets/      → Presentaciones, capturas, vídeos, logo
├── devtools/    → Generadores, conversores, migraciones
├── sandbox/     → Prototipos y experimentos (nunca producción)
├── scripts/
├── installer/
├── build/
└── dist/
```

## REGLA Nº2 — El Core nunca cambia

```
CORE
├── geometry
├── project
├── engine
├── logger
├── config
├── pk
└── buffer
```

Ningún plugin o módulo externo puede modificar el Core.  
El Core es la base estable sobre la que crece todo el proyecto.

## REGLA Nº3 — Specs first

Nada entra en `src/` hasta que haya pasado por `specs/`.  
Primero se diseña (use cases, diagramas, protocolos), luego se implementa.

## Niveles del proyecto

| Nivel   | Descripción                              | Ejemplos                     |
|---------|------------------------------------------|------------------------------|
| CORE    | Base estable, nunca cambia               | geometry, project, engine    |
| PLUGINS | Módulos intercambiables y extensibles    | catastro, roads, excel, dxf  |
| SDK     | API pública para desarrollo de plugins   | interfaces, protocolos       |

## Estructura de cada plugin

```
plugins/roads/
├── __init__.py
├── controller.py
├── services.py
├── models.py
├── repository.py
├── exporter.py
├── settings.py
└── tests.py
```
