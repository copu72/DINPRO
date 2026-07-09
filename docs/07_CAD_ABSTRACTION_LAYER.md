# CAD Abstraction Layer (CAL) — v0.2.0

## Propósito

Aislar a DINPRO de cualquier CAD específico. El programa no sabe si el eje viene de AutoCAD, DXF o BricsCAD.

## Arquitectura

```
DINPRO Project
      │
      ▼
 CADAdapter (abstract)
      │
      ├── DXFAdapter      → Lee archivos .dxf sin dependencias externas
      └── AutoCADAdapter  → COM via pywin32 (requiere AutoCAD instalado)
```

## Módulos

| Módulo | Archivo | Propósito |
|--------|---------|-----------|
| `CADAdapter` | `cad/base/cad_adapter.py` | Clase abstracta. Contrato que todo adaptador debe cumplir. |
| `DXFAdapter` | `cad/dxf/dxf_adapter.py` | Lee DXF con parser propio (sin dependencias). |
| `AutoCADAdapter` | `cad/autocad/autocad_adapter.py` | COM via pywin32. Stub preparado para uso real. |
| `Entity models` | `cad/base/entity.py` | Line, Polyline, Circle, Text, Block, Layer, BlockAttribute. |
| `Selection` | `cad/base/selection.py` | Contenedor de selección. Método `as_axis_data()` para convertir a eje. |
| `Factory` | `cad/factory.py` | `open_cad(path)` → adaptador según extensión (.dxf, .dwg). |

## Entidades

Todas las entidades heredan de `Entity` con: handle, layer, color, linetype, lineweight, visible.

- **Line** — start, end, length (auto-calculado)
- **Polyline** — vertices 3D, closed, elevation, length (auto), to_2d()
- **Circle** — center, radius, length
- **Text** — content, insertion, height, rotation, is_mtext
- **Block** — name, insertion, rotation, scale, attributes
- **Layer** — name, color, linetype, locked, frozen

## DXF Parser

Parser DXF propio. No requiere dependencias externas. Soporta:

- LINE, LWPOLYLINE, POLYLINE, CIRCLE, TEXT, MTEXT
- Capas (TABLES/SECTION)
- Atributos de bloque (BLOCK)

## Proyecto .din

El formato de proyecto nativo de DINPRO. Archivo JSON con extensión `.din`.

Almacena:
- Versión de DINPRO
- Ruta del archivo CAD vinculado
- Configuración (settings)
- Eje (vértices, CRS, longitud)
- Resultados de módulos
- Metadatos del proyecto

```python
from dinpro import Project

project = Project("proyecto.din")
project.start()
project.open("trazado.dxf")  # Vincula CAD y carga el eje
project.save()               # Guarda como proyecto.din
project.close()              # Auto-guarda antes de cerrar
```

## Tests

- 152 tests unitarios
- Cobertura CAL (sin AutoCAD): > 90 %
- DXF real de prueba en `tests/data/test.dxf`
