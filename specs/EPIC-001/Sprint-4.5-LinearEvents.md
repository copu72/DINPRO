# Sprint 4.5 — LinearEvents

## Objetivo

Implementar el modelo de eventos lineales versionados que permite asociar información de negocio al eje referenciado. Este sprint es el puente entre la geometría pura (Sprints 4.1–4.4) y los módulos funcionales (Municipios, Carreteras, Catastro, etc.).

## Artefactos a implementar

### 1. `LinearEvent` — Value Object (inmutable, versionado)

```python
@dataclass(frozen=True)
class LinearEvent:
    _event_id: str      # UUID, estable
    _event_type: str    # "municipio", "carretera", "rio", "parcela", etc.
    _pk_start: Station
    _pk_end: Station
    _attributes: dict[str, Any]
    _geometry: Polyline | None  # geometría del subtramo (opcional)
    _version: int               # 1, 2, 3, ... (inmutable por instancia)
    _revision: str              # hash SHA256 de contenido
    _created_at: str            # ISO 8601
    _updated_at: str            # ISO 8601
    _metadata: dict[str, Any]
```

**Propiedades públicas:**

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `e.event_id` | `str` | Identificador único estable |
| `e.event_type` | `str` | Tipo semántico del evento |
| `e.pk_start` | `Station` | PK inicial |
| `e.pk_end` | `Station` | PK final |
| `e.attributes` | `dict` | Atributos de negocio (copia) |
| `e.geometry` | `Polyline | None` | Geometría asociada |
| `e.version` | `int` | Versión actual |
| `e.revision` | `str` | Hash de contenido |
| `e.created_at` | `str` | Timestamp de creación |
| `e.updated_at` | `str` | Timestamp de última modificación |
| `e.metadata` | `dict` | Metadatos (copia) |
| `e.length` | `float` | Longitud en metros |

**Reglas de dominio:**

- `pk_start < pk_end` (validado en `__post_init__`)
- `event_type` debe ser un identificador alfanumérico simple
- `revision` se genera automáticamente como `SHA256(pk_start|pk_end|attributes|event_type|version)`
- `attributes` y `metadata` se almacenan frozen, se acceden como copia

### 2. `LinearEventSet` — Aggregate Root

```python
class LinearEventSet:
    def __init__(self, axis: Axis) -> None
```

**API pública:**

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `les.add(event_type, pk_start, pk_end, attributes, geometry, metadata)` | `LinearEvent` | Crea y añade un nuevo evento (version=1) |
| `les.remove(event_id)` | `None` | Elimina un evento por ID |
| `les.update(event_id, ...)` | `LinearEvent` | Crea nueva versión del evento |
| `les.get(event_id)` | `LinearEvent` | Obtiene evento por ID |
| `les.query(event_type=None)` | `list[LinearEvent]` | Filtra por tipo (o todos) |
| `les.query_range(pk_start, pk_end)` | `list[LinearEvent]` | Eventos que intersectan el rango PK |
| `les.overlaps(event_id)` | `list[LinearEvent]` | Eventos que solapan con el dado |
| `les.gaps(event_type)` | `list[tuple[Station, Station]]` | Huecos sin cobertura para un tipo |
| `les.audit_trail(event_id)` | `list[LinearEvent]` | Historial completo de versiones |
| `les.events` | `list[LinearEvent]` | Todos los events activos |
| `les.axis` | `Axis` | Eje de referencia |
| `les.count` | `int` | Número de eventos activos |

**Reglas de dominio:**

- `update()` incrementa `version`, recalcula `revision`, actualiza `updated_at`
- `remove()` no destruye: marca como obsoleto o elimina (según política)
- `gaps()` devuelve intervalos PK sin eventos de un tipo dado
- `overlaps()` usa intersección PK-PK (misma lógica que `Segment.intersects`)
- Todos los eventos comparten el mismo `axis`
- No hay dependencia de SQE ni de GIS

### 3. `EventCollection` — Colección por tipo (opcional, helper)

```python
class EventCollection:
    def __init__(self, event_type: str) -> None
```

| Método | Retorno |
|--------|---------|
| `ec.add(event)` | `None` |
| `ec.remove(event_id)` | `None` |
| `ec.by_range(pk_start, pk_end)` | `list[LinearEvent]` |
| `ec.overlaps(event)` | `list[LinearEvent]` |
| `ec.gaps()` | `list[tuple[Station, Station]]` |
| `ec.all()` | `list[LinearEvent]` |

## Criterios de aceptación

- [ ] `LinearEvent` es un `@dataclass(frozen=True)` con todas las propiedades definidas
- [ ] `LinearEvent.revision` es un hash SHA256 estable del contenido
- [ ] `LinearEventSet.add()` funciona con y sin geometría
- [ ] `LinearEventSet.update()` incrementa versión y actualiza timestamp
- [ ] `LinearEventSet.remove()` elimina el evento activo
- [ ] `LinearEventSet.query_range()` devuelve solo eventos que intersectan el rango
- [ ] `LinearEventSet.overlaps()` detecta solapamientos correctamente
- [ ] `LinearEventSet.gaps()` identifica huecos sin cobertura
- [ ] `LinearEventSet.audit_trail()` devuelve todas las versiones
- [ ] Los eventos almacenan copias de `attributes` y `metadata` (inmutabilidad)
- [ ] Cobertura de tests ≥ 90%
- [ ] ruff: 0 errores, mypy: 0 errores
- [ ] No se rompen tests existentes (0 regresiones)

## Estimación

- **Archivos nuevos:** `linear_event.py`, `linear_event_set.py`, `event_collection.py`
- **Tests:** `test_lre_linear_event.py`, `test_lre_linear_event_set.py`, `test_lre_event_collection.py`
- **Tests esperados:** ~80–120
- **Cobertura objetivo:** ≥ 90%

## Dependencias

- stdlib: `uuid`, `hashlib`, `datetime`, `copy`, `dataclasses`
- Internas: `Station`, `Segment`, `Axis`, `Polyline`

## Precedencia

Este sprint **debe completarse antes** que:
- Sprint 4.6 (RouteCalibration) — los eventos lineales serán la entrada
- Sprint 4.7 (LongitudinalProfile) — opcional pero recomendado
- Sprint 4.8 (Exporter) — exportará eventos
- Sprint 4.9 (Integration) — integrará todo
- Módulos Municipios, Carreteras, Ríos, Catastro — heredarán de LinearEvent

## Impacto en el LRE

```
LinearEventSet
    ├── add()        → crea evento version 1
    ├── update()     → nueva version del mismo event_id
    ├── remove()     → elimina activo
    ├── query()      → filtro por tipo
    ├── query_range()→ filtro por rango PK
    ├── overlaps()   → deteccion de solapamiento
    └── gaps()       → huecos sin cobertura
```

## Riesgos

- **Ninguno conocido.** El diseño está aislado, sin dependencias externas, y sigue el mismo patrón que Segment/DynamicSegmentation.
