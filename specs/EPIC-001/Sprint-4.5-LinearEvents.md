# Sprint 4.5 — LinearEvents

## Objetivo

Implementar el modelo de eventos lineales versionados que permite asociar información de dominio al eje referenciado. Este sprint es el puente entre la geometría pura (Sprints 4.1–4.4) y los módulos funcionales (Municipios, Carreteras, Hidrografía, Catastro, Infraestructuras, Medio Ambiente, etc.).

A partir de este sprint, DINPRO deja de gestionar únicamente geometría para gestionar **conocimiento del dominio**.

## Principios arquitectónicos (DA-005 a DA-009)

| Código | Decisión |
|--------|----------|
| **DA-005** | `LinearEvent` representa **hechos del dominio** asociados a un intervalo PK. Nunca contiene lógica geométrica — toda geometría pertenece al GSE. |
| **DA-006** | Los eventos son **inmutables**. Cada modificación genera una nueva instancia (versionado inmutable). |
| **DA-007** | `LinearEventSet` es un **Aggregate Root**, no una colección. Expone operaciones de dominio: `filter()`, `sort()`, `merge()`, `split()`, `group_by()`, `statistics()`. |
| **DA-008** | Todo evento tiene **identidad estable** (`event_id`). La igualdad se define por `event_id` + `version`. |
| **DA-009** | La auditoría pertenece a `EventMetadata`, nunca al evento principal. |

## Enums del dominio

```python
class EventType(Enum):
    """Tipo semántico del evento. Extensible por los módulos funcionales."""
    UNDEFINED = "undefined"
    # Los valores concretos se definen en los módulos:
    # MUNICIPIO, CARRETERA, RIO, PARCELA, SERVIDUMBRE, ZONA_PROTEGIDA, ...

class EventSource(Enum):
    """Origen del evento."""
    MANUAL = "manual"
    SQE = "sqe"
    IMPORT = "import"
    CATALOGO = "catalogo"
    API = "api"
    MIGRATION = "migration"

class EventStatus(Enum):
    """Estado del evento. Sin booleanos — preparado para auditoría."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    DELETED = "deleted"
```

## Modelo de dominio

### `EventMetadata` — Metadatos de auditoría (separados del evento)

```python
@dataclass(frozen=True)
class EventMetadata:
    source: EventSource = EventSource.MANUAL
    status: EventStatus = EventStatus.ACTIVE
    version: int = 1
    revision: str = ""               # SHA256 de contenido, auto
    created_at: str = ""              # ISO 8601, auto
    created_by: str = "system"
    updated_at: str = ""              # ISO 8601, auto
    confidence: float = 1.0           # 0.0 - 1.0
    tags: tuple[str, ...] = ()
    notes: str = ""
```

### `EventReference` — Referencia a entidad externa (preparado para futuro)

```python
@dataclass(frozen=True)
class EventReference:
    ref_type: str     # "municipio", "carretera", "parcela", "linea", "rio", ...
    ref_id: str       # ID en el sistema externo
    provider: str     # "catastro", "ign", "dgt", ...
```

Un `LinearEvent` puede tener cero o más `EventReference`.

### `LinearEvent` — Hecho del dominio asociado a un intervalo PK

```python
@dataclass(frozen=True)
class LinearEvent:
    _event_id: str                    # UUID, generado una vez — identidad estable
    _event_type: EventType            # Enum, no string
    _axis: Axis                       # Contexto: el event sabe a qué eje pertenece
    _segment: Segment | None          # Subtramo del eje (geometry + stations)
    _attributes: dict[str, Any]       # Atributos de negocio del hecho representado
    _metadata: EventMetadata          # Auditoría separada (DA-009)
    _references: tuple[EventReference, ...] = ()  # Referencias a entidades externas
```

**Propiedades públicas:**

| Propiedad | Tipo | Origen |
|-----------|------|--------|
| `e.event_id` | `str` | Directo |
| `e.event_type` | `EventType` | Directo |
| `e.axis` | `Axis` | Directo |
| `e.station_start` | `Station` | Derivado de `segment` |
| `e.station_end` | `Station` | Derivado de `segment` |
| `e.geometry` | `Polyline | None` | Derivado de `segment` |
| `e.length` | `float` | Derivado de `segment` |
| `e.attributes` | `dict` | Copia defensiva |
| `e.metadata` | `EventMetadata` | Directo |
| `e.references` | `tuple[EventReference]` | Directo |

**Identidad y criterio de igualdad (DA-008):**

- `event_id` identifica unívocamente el **hecho del mundo real** (ej: "tramo de la M-40 entre PK 12 y PK 18").
- `event_id` + `version` identifica una **versión específica** del hecho.
- `LinearEvent(a, v1) == LinearEvent(a, v2)` es `False` aunque compartan `event_id` — son versiones distintas.
- `LinearEvent(a, v1) == LinearEvent(a, v1)` es `True` solo si todos los campos son iguales.

**Política de versionado (DA-006):**

- Cada modificación (vía `LinearEventSet.update()`) crea un nuevo `LinearEvent` con `version = previous + 1`.
- Las versiones anteriores se conservan en el `audit_trail`.
- No hay modificación in-situ. Inmutabilidad estricta.

**Política de solapamientos (delegada al dominio):**

- `LinearEventSet` detecta y reporta solapamientos (misma lógica que `Segment.intersects`).
- La decisión de si dos eventos del mismo tipo pueden solaparse corresponde al **módulo funcional**, no al LRE.
- Ejemplo: dos municipios NO pueden solaparse; dos afecciones ambientales SÍ pueden.

### `LinearEventSet` — Aggregate Root

```python
class LinearEventSet:
    def __init__(self, axis: Axis) -> None
```

**API de ciclo de vida:**

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `les.add(event_type, segment, attributes, source, references, ...)` | `LinearEvent` | Crea evento version=1, metadata auto |
| `les.update(event_id, attributes=..., segment=..., ...)` | `LinearEvent` | Crea nueva versión (v=n+1) |
| `les.remove(event_id)` | `None` | Marca como DELETED (no destruye) |
| `les.get(event_id)` | `LinearEvent | None` | Devuelve la versión activa |
| `les.get_version(event_id, version)` | `LinearEvent | None` | Devuelve una versión específica |

**API de consulta:**

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `les.filter(event_type=None, status=ACTIVE)` | `LinearEventSet` | Nuevo set con filtro aplicado |
| `les.query_range(pk_start, pk_end)` | `list[LinearEvent]` | Eventos activos que intersectan el rango |
| `les.overlaps(event_id)` | `list[LinearEvent]` | Eventos activos que solapan con el dado |
| `les.gaps(event_type)` | `list[tuple[Station, Station]]` | Intervalos PK sin cobertura |
| `les.audit_trail(event_id)` | `list[LinearEvent]` | Todas las versiones del evento |

**API de análisis:**

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `les.sort(by="pk_start")` | `LinearEventSet` | Nuevo set ordenado |
| `les.merge(other)` | `LinearEventSet` | Fusión con otro set (mismo axis) |
| `les.split(event_id, pk_split)` | `tuple[LinearEvent, LinearEvent]` | Divide un evento en dos |
| `les.group_by(event_type)` | `dict[EventType, list[LinearEvent]]` | Agrupación por tipo |
| `les.statistics()` | `dict` | Métricas: count, cobertura, solapes, gaps totales |

**Reglas de dominio:**

- Todas las operaciones devuelven nuevas instancias o lists (inmutabilidad del set).
- `merge()` solo acepta sets del mismo `axis`.
- `split()` genera dos eventos con el mismo `event_id` (raíz) y versiones incrementadas.
- `filter()` por `status=ACTIVE` es el default — filtrar por `DELETED` requiere query explícita.

## Archivos a implementar

| Archivo | Clases |
|---------|--------|
| `event_type.py` | `EventType`, `EventSource`, `EventStatus` |
| `event_metadata.py` | `EventMetadata` |
| `event_reference.py` | `EventReference` |
| `linear_event.py` | `LinearEvent` |
| `linear_event_set.py` | `LinearEventSet` |

## Dependencias

- stdlib: `uuid`, `hashlib`, `datetime`, `copy`, `dataclasses`, `enum`
- Internas LRE: `Station`, `Segment`, `Axis`, `Polyline`
- **No depende de:** SQE, GIS, módulos funcionales, bases de datos

## Criterios de aceptación

- [ ] `EventType`, `EventSource`, `EventStatus` son `Enum` con valores definidos
- [ ] `EventMetadata` es `@dataclass(frozen=True)` con valores por defecto sensatos
- [ ] `EventReference` es `@dataclass(frozen=True)`
- [ ] `LinearEvent` es `@dataclass(frozen=True)` con `event_id` como identidad estable
- [ ] `LinearEvent.station_start`/`station_end` se derivan de `segment`
- [ ] `LinearEvent.attributes` devuelve copia (inmutabilidad)
- [ ] `LinearEventSet.add()` crea versión 1 con `EventStatus.ACTIVE`
- [ ] `LinearEventSet.update()` incrementa versión, preserva versiones anteriores
- [ ] `LinearEventSet.remove()` marca como `DELETED`, no destruye
- [ ] `LinearEventSet.filter()` devuelve un nuevo `LinearEventSet`
- [ ] `LinearEventSet.query_range()` intersecta correctamente
- [ ] `LinearEventSet.overlaps()` usa `Segment.intersects`
- [ ] `LinearEventSet.gaps()` identifica huecos PK sin cobertura
- [ ] `LinearEventSet.audit_trail()` devuelve todas las versiones
- [ ] `LinearEventSet.merge()` rechaza sets de distinto `axis`
- [ ] `LinearEventSet.split()` preserva `event_id`, versiona
- [ ] `LinearEventSet.statistics()` es funcional
- [ ] Cobertura de tests ≥ 90%
- [ ] ruff: 0 errores, mypy: 0 errores
- [ ] 0 regresiones en tests existentes

## Estimación

- **Archivos nuevos:** 5 (`event_type.py`, `event_metadata.py`, `event_reference.py`, `linear_event.py`, `linear_event_set.py`)
- **Archivos de tests:** 3 (`test_lre_event_types.py`, `test_lre_linear_event.py`, `test_lre_linear_event_set.py`)
- **Tests esperados:** ~120–160
- **Cobertura objetivo:** ≥ 90%

## Impacto arquitectónico

```
GSE (geometría)
  ↓
LRE (Station, Segment, MeasureSystem, LateralProjection, DynamicSegmentation)
  ↓
LinearEventSet ←── Aggregate Root (DA-007)
  ├── add / update / remove
  ├── filter / sort / merge / split / group_by
  ├── query_range / overlaps / gaps
  └── audit_trail / statistics
        ↓
Módulos funcionales (producen eventos):
  ├── Municipios     → EventType("municipio")
  ├── Carreteras     → EventType("carretera")
  ├── Hidrografía    → EventType("rio")
  ├── Catastro       → EventType("parcela")
  ├── Infraestructuras → EventType("servidumbre")
  └── ...
        ↓
Analysis Pipeline (consume eventos, sin conocer origen)
```

## Riesgos mitigados

| Riesgo (review) | Mitigación |
|-----------------|------------|
| Versionado no definido | DA-006: versionado inmutable |
| Identidad no definida | DA-008: `event_id` + `version` |
| Solapamientos no definidos | Política delegada al dominio, `LinearEventSet` solo detecta |
| Strings como tipos | `EventType`, `EventSource`, `EventStatus` como Enum |
| Auditoría mezclada | `EventMetadata` separado (DA-009) |
| Lógica geométrica en eventos | DA-005: toda geometría en GSE |
