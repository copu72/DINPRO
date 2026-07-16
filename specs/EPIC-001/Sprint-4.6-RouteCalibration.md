# Sprint 4.6 — RouteCalibration

## RFC — Request for Comments

**Estado:** Borrador para Architect Review
**Depende de:** D-13 a D-18, DA-010, DA-011 (aprobados en sesión de diseño)
**Precede a:** Sprint 4.7 LongitudinalProfile, Sprint 4.8 Exporter

---

## 1. Problema

La distancia geométrica medida sobre un eje (Polyline) y el PK oficial de una carretera, ferrocarril o conducción rara vez coinciden. Las causas incluyen:

- Errores de medición topográfica original
- Modificaciones de trazado sin recalcular PK
- Convenciones administrativas (ej: un kilómetro oficial ≠ 1000 m geométricos)
- Discontinuidades por variantes o bypass

**RouteCalibration resuelve:** definir y consultar la correspondencia entre distancia geométrica y PK oficial mediante una función a tramos lineales.

---

## 2. Modelo matemático

### 2.1 Definición

Dados `n` puntos de calibración ordenados estrictamente por distancia geométrica:

```
(d_0, s_0), (d_1, s_1), ..., (d_{n-1}, s_{n-1})
```

donde `d_i` = distancia acumulada en metros sobre la geometría del eje, `s_i` = Station (PK oficial).

### 2.2 Interpolación lineal

Para `d_i ≤ d ≤ d_{i+1}`:

```
f(d) = s_i + (d - d_i) * (s_{i+1} - s_i) / (d_{i+1} - d_i)
```

Para `s` entre `s_i` y `s_{i+1}` (inversa):

```
f⁻¹(s) = d_i + (s - s_i) * (d_{i+1} - d_i) / (s_{i+1} - s_i)
```

Si `s_i > s_{i+1}` (PK decreciente), la fórmula funciona igual — pendiente negativa.

### 2.3 Extrapolación

Por debajo del primer punto o por encima del último:

| Modo | Comportamiento |
|------|---------------|
| `NONE` | Lanza `CalibrationError` |
| `LINEAR` | Extiende la pendiente del tramo más cercano |
| `CONSTANT` | Mantiene la estación del punto extremo |

### 2.4 Discontinuidades

Una discontinuidad NO implica un salto en geometría. Es una propiedad del sistema de medida:

- El eje (`Axis`) es continuo
- La correspondencia estación-oficial → distancia puede tener rangos no definidos

Ejemplo: PK 5+000 → PK 8+000 sin puntos de control intermedios. La calibración solo es válida dentro del rango `[d_0, d_{n-1}]`.

---

## 3. Modelo de dominio

### 3.1 Value Objects

```python
@dataclass(frozen=True)
class CalibrationPoint:
    distance: float          # metros sobre geometría del eje
    station: Station         # PK oficial
    source: str = "manual"
    confidence: float = 1.0

class ExtrapolationMode(Enum):
    NONE = "none"
    LINEAR = "linear"
    CONSTANT = "constant"

class CalibrationIssue(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
```

### 3.2 CalibrationSet

```python
@dataclass(frozen=True)
class CalibrationSet:
    campaign_id: str
    axis: Axis
    points: tuple[CalibrationPoint, ...]
    created_at: str = ""       # ISO 8601, auto
    source: str = "manual"
```

**Validación en `__post_init__`:**

- `points` no vacío
- `distance` estrictamente creciente (DA-010)
- Ningún `station.value` infinito o NaN
- `confidence` en [0.0, 1.0]

### 3.3 RouteCalibration — Aggregate Root

```python
class RouteCalibration:
    def __init__(
        self,
        axis: Axis,
        calibration_sets: Sequence[CalibrationSet],
        default_campaign: str | None = None,
    ) -> None
```

#### API pública

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `rc.station_at_distance(d, mode=NONE)` | `Station` | Distancia geométrica → PK oficial |
| `rc.distance_at_station(s, mode=NONE)` | `float` | PK oficial → distancia geométrica |
| `rc.interpolate(d)` | `Station` | Sin extrapolación (equivale a `mode=NONE`) |
| `rc.extrapolate(d)` | `Station` | Con extrapolación (equivale a `mode=LINEAR`) |
| `rc.validate()` | `list[CalibrationIssue]` | Validación del set activo |
| `rc.calibration_sets` | `list[CalibrationSet]` | Todos los sets registrados |
| `rc.active_set` | `CalibrationSet` | Set activo (default o explicitado) |
| `rc.axis` | `Axis` | Eje de referencia |

#### Reglas de dominio

- `station_at_distance()` y `distance_at_station()` son simétricas (D-13)
- Si `d` está fuera del rango calibrado y `mode=NONE` → `CalibrationError`
- Si `mode=LINEAR` o `CONSTANT` → extrapola sin error
- PK decrecientes permitidos (D-15), con `WARNING` en `validate()`
- La geometría nunca se modifica (DA-011)
- Múltiples campañas conviven; `default_campaign` selecciona el set activo (D-16)

---

## 4. Relación con MeasureSystem

`MeasureSystem` (Sprint 4.1) se mantiene como **facade** (D-17):

```
MeasureSystem (v4.1, facade)
    └── RouteCalibration (v4.6, implementación real)
```

Internamente, `MeasureSystem` delegará en `RouteCalibration`. Esto asegura:

- Compatibilidad hacia atrás sin cambios en consumidores existentes
- Una sola fuente de verdad para la lógica de calibración
- Migración opcional para nuevos consumidores

---

## 5. Dependencias

- stdlib: `bisect`, `dataclasses`, `enum`, `datetime`
- Internas LRE: `Axis`, `Station`
- No depende de: SQE, GIS, módulos funcionales

---

## 6. Arquitectura general

```
Axis (GSE)
  │
  ├── MeasureSystem (v4.1, facade → RC)
  │
  └── RouteCalibration (v4.6)
        └── CalibrationSet
              └── CalibrationPoint
                    ├── distance (float)
                    ├── station (Station)
                    ├── source (str)
                    └── confidence (float)
                          │
                          ▼
                    LinearEvent (opcional, para exportación)
```

---

## 7. Precedencia

Este sprint debe completarse **antes** que:

- Sprint 4.7 LongitudinalProfile (consume estaciones calibradas)
- Sprint 4.8 Exporter (exporta calibraciones como eventos)
- Sprint 4.9 Integration (integra con MeasureSystem facade)
- Módulos Municipios, Carreteras (requieren PK real, no geométrico)

---

## SPEC — Criterios de aceptación

- [ ] `CalibrationPoint` es `@dataclass(frozen=True)` con `distance`, `station`, `source`, `confidence`
- [ ] `CalibrationSet` valida monotonicidad estricta de `distance` (DA-010)
- [ ] `CalibrationSet` valida `confidence` en [0.0, 1.0]
- [ ] `CalibrationSet` rechaza puntos vacíos
- [ ] `RouteCalibration.__init__` acepta `Sequence[CalibrationSet]` y `default_campaign`
- [ ] `station_at_distance()` con `mode=NONE` en rango → Station correcta
- [ ] `station_at_distance()` con `mode=NONE` fuera de rango → `CalibrationError`
- [ ] `station_at_distance()` con `mode=LINEAR` fuera de rango → extrapola
- [ ] `distance_at_station()` es inversa de `station_at_distance()`
- [ ] PK decrecientes se interpolan correctamente
- [ ] `validate()` devuelve issues con severidad `INFO`, `WARNING`, `ERROR`
- [ ] Geometría eje no se modifica tras calibración (DA-011)
- [ ] Múltiples `CalibrationSet` coexisten, `active_set` respeta `default_campaign`
- [ ] Cobertura ≥ 90%
- [ ] ruff: 0 errores
- [ ] mypy: 0 errores
- [ ] 0 regresiones en tests existentes

---

## Estimación

| Archivo | Clases | Tests |
|---------|--------|-------|
| `calibration_point.py` | `CalibrationPoint` | ~15 |
| `extrapolation_mode.py` | `ExtrapolationMode` | ~5 |
| `calibration_issue.py` | `CalibrationIssue` | ~5 |
| `calibration_set.py` | `CalibrationSet` | ~30 |
| `route_calibration.py` | `RouteCalibration` | ~60 |
| `test_*.py` | — | ~115 |

---

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Rotura de consumidores de MeasureSystem | D-17: facade; compatibilidad garantizada |
| Extrapolación incorrecta en casos extremos | D-18: tres modos explícitos, validables uno a uno |
| Rendimiento con miles de puntos | Búsqueda O(log n) `bisect`, interpolación O(1) |
