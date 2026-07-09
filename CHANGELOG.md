# Changelog

## [0.2.0] - 2026-07-09

### Added
- CAD Abstraction Layer (CAL): cad/base, cad/dxf, cad/autocad
- Entity models: Line, Polyline, Circle, Text, Block, Layer, BlockAttribute
- DXFAdapter: parser propio sin dependencias (LINE, LWPOLYLINE, CIRCLE, TEXT, MTEXT, capas)
- AutoCADAdapter: COM via pywin32 (stub listo para uso con AutoCAD instalado)
- CAD Factory: `open_cad(path)` → adaptador según extensión
- Selection system con `as_axis_data()` para carga automática de ejes
- Formato `.din`: proyecto nativo DINPRO (JSON, guarda CAD vinculado, settings, eje, resultados)
- Project.save_as() con extensión `.din` automática
- Project.close() auto-guarda antes de cerrar
- Project.open() compatible con .dxf, .dwg y .din
- 41 nuevos tests (152 total)
- Documentación: docs/07_CAD_ABSTRACTION_LAYER.md

### Changed
- Version bump: 0.1.0 → 0.2.0
- Project.start() restaura proyecto .din si existe

## [0.1.0] - 2026-07-09

### Added
- Paquete `dinpro` instalable (`src/dinpro/`)
- Core completo: 11 clases fundamentales
- 111 tests unitarios, cobertura 91 %
- Configuración de ruff, black, isort, mypy, pytest

## [0.0.1] - 2026-07-09

### Added
- Estructura completa del repositorio
- Documentación fundacional
