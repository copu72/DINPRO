# LRE Public API

Versión de referencia: `v0.4.0-sprint-4.4`

## 1. Station

```python
Station(value: float)  # Value Object, frozen, @dataclass
```

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `s.value` | `float` | Valor del PK en metros |
| `s.parse(text, format="Classic")` | `Station` | Parseo: `"PK 12+350"` → `Station(12350)` |
| `s.format(format="Classic")` | `str` | Formato: `Station(12350)` → `"PK 12+350.000"` |

**Contrato:** `Station(a) == Station(b)` si y solo si `a == b`.

---

## 2. MeasureSystem

```python
MeasureSystem(axis: Axis)  # Domain Service
```

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `ms.measure(pk: float)` | `MeasureResult` | Convierte PK de obra a PK real |
| `ms.reverse_measure(real: float)` | `MeasureResult` | Convierte PK real a PK de obra |
| `ms.is_continuous(pk: float)` | `bool` | Verifica si un PK está en zona continua |
| `ms.calibrations` | `list[CalibrationPoint]` | Puntos de calibración registrados |
| `ms.discontinuities` | `list[MeasureDiscontinuity]` | Discontinuidades registradas |

### MeasureResult

```python
MeasureResult(reference: float, real: float, discontinuity: bool, gap: float)
```

### CalibrationPoint

```python
CalibrationPoint(reference: float, real: float, source: str)
```

### MeasureDiscontinuity

```python
MeasureDiscontinuity(local: float, real: float, gap: float, type: str)
```

**Contrato:** `MeasureSystem` es un Domain Service, no una utilidad. Soporta calibraciones, discontinuidades y resets de PK. Trabaja con múltiples sistemas de medida desde el diseño inicial.

---

## 3. LateralProjection

```python
LateralProjection(axis: Axis)  # Domain Service
```

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `lp.offset_point(pk, distance, side)` | `Point` | Punto desplazado lateralmente |
| `lp.cross_section(pk, width, steps)` | `Polyline` | Sección transversal |
| `lp.corridor(pk_start, pk_end, half_width, steps)` | `Polygon` | Corredor bilateral |
| `lp.project_to_axis(point)` | `ProjectionResult` | Proyecta punto al eje |
| `lp.nearest_pk(point)` | `ProjectionResult` | PK más cercano a punto |

### ProjectionResult

```python
ProjectionResult(pk: float, point: Point, distance: float, side: str)
```

**Contrato:** Trabaja exclusivamente con el `Axis`, no conoce GIS ni SQE.

---

## 4. Segment

```python
Segment(axis, start, end, geometry, ...)  # Value Object, frozen, @dataclass
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `s.id` | `str` | Identificador único (estable) |
| `s.axis` | `Axis` | Eje de referencia |
| `s.station_start` | `Station` | PK de inicio |
| `s.station_end` | `Station` | PK de fin |
| `s.geometry` | `Polyline` | Geometría del subtramo |
| `s.length` | `float` | Longitud en metros |
| `s.attributes` | `dict` | Atributos del segmento |
| `s.metadata` | `dict` | Metadatos del segmento |

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `s.contains(station)` | `bool` | ¿El PK está dentro del segmento? |
| `s.intersects(other)` | `bool` | ¿Hay solapamiento con otro segmento? |
| `s.reverse()` | `Segment` | Invierte la geometría (no cambia el intervalo de PK) |
| `s.clip(start, end)` | `Segment` | Recorta el segmento a un subintervalo |
| `s.offset(distance, steps)` | `Polygon` | Genera corredor bilateral simétrico |
| `s.to_axis()` | `Axis` | Convierte el segmento en un nuevo eje |

**Contrato:** Segment es inmutable — toda operación devuelve una nueva instancia.

---

## 5. DynamicSegmentation

```python
DynamicSegmentation(axis: Axis)  # Domain Service
```

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `ds.segment(start, end)` | `Segment` | Crea un segmento entre dos estaciones |
| `ds.split(stations)` | `list[Segment]` | Divide el eje en segmentos por PKs |
| `ds.merge(segments)` | `Segment` | Fusiona segmentos contiguos |

**Contrato:** Trabaja únicamente con `Axis`, `Station`, `MeasureSystem` y `LateralProjection`. No conoce GIS ni SQE.

---

## Contratos transversales

1. **Inmutabilidad:** Todos los Value Object son `@dataclass(frozen=True)`.
2. **Sin dependencias GIS:** El LRE no importa ni conoce nada de GIS.
3. **Sin dependencias externas:** Cero dependencias runtime externas al proyecto.
4. **Sin knowledge del dominio de negocio:** El LRE no conoce municipios, carreteras, ríos, ni catastro.
5. **Serialización:** Todos los objetos soportan `__repr__`, `__eq__`, `__hash__`.

---

## Diagrama de dependencias

```
Axis
  ├── MeasureSystem
  ├── Station
  │     ├── StationParser
  │     └── StationFormatter
  ├── LateralProjection
  └── DynamicSegmentation
        └── Segment
              └── _extract_subpolyline (internal)
```

---

*Este documento es de referencia. Cualquier cambio en la API pública debe reflejarse aquí y pasar por Architect Review.*
