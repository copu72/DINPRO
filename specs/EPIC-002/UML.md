# EPIC-002 — Spatial Query Engine (UML)

**Versión:** 0.1
**Estado:** Preliminar

---

## 1. Diagrama de clases

```
┌─────────────────────────────────────────────────────────────────┐
│                    SpatialQueryEngine                            │
├─────────────────────────────────────────────────────────────────┤
│ - _axis: Axis                                                    │
│ - _lateral: LateralProjection | None                              │
│ - _index: dict[str, IndexedFeature]                              │
├─────────────────────────────────────────────────────────────────┤
│ + index(features: list[IndexedFeature]) -> None                   │
│ + index_from_geometries(...) -> None                              │
│ + intersect_axis() -> list[LinearIntersection]                    │
│ + intersect_corridor(half_width, steps) -> list[LinearIntersection]│
│ + intersect_range(pk_start, pk_end, half_width) -> list[...]      │
│ + count() -> int                                                  │
│ + get_by_id(feature_id) -> IndexedFeature | None                  │
│ + clear() -> None                                                 │
│ + to_events(intersections, event_type) -> list[LinearEvent]       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
┌─────────────────┐ ┌─────────────────────┐ ┌─────────────────┐
│  IndexedFeature  │ │ LinearIntersection   │ │   LinearEvent    │
├─────────────────┤ ├─────────────────────┤ ├─────────────────┤
│ + geometry      │ │ + feature            │ │ + pk_start      │
│ + properties    │ │ + entry_pk           │ │ + pk_end        │
│ + id            │ │ + exit_pk            │ │ + event_type    │
└─────────────────┘ │ + entry_point        │ │ + properties    │
                    │ + exit_point         │ └─────────────────┘
                    │ + affected_length    │
                    └─────────────────────┘

                         ▲
                         │
                    ┌────┴────┐
                    │ Geometry│ (de GSE)
                    ├─────────┤
                    │ Point   │
                    │ Polyline│
                    │ Polygon │
                    └─────────┘

                         ▲
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
┌─────────────────────────┐ ┌──────────────────────┐
│   _SpatialScanner        │ │  _IntersectionDetector│
│   (interno)              │ │  (interno)            │
├─────────────────────────┤ ├──────────────────────┤
│ + scan(axis, corridor)  │ │ + detect(axis_geom,  │
│   -> list[Intersection]  │ │   target) -> list[   │
└─────────────────────────┘ │   (float, float)]    │
                           └──────────────────────┘
```

## 2. Flujo de intersección

```
Axis (LRE)
    │
    ▼
SpatialQueryEngine.intersect_corridor(half_width=50)
    │
    ├── 1. LateralProjection.corridor(0, length, 50)
    │       └── Polygon (corredor)
    │
    ├── 2. _SpatialScanner.scan(axis, corridor)
    │       │
    │       ├── Por cada geometría indexada:
    │       │   ├── ¿Polygon vs Polygon? → intersección geométrica
    │       │   ├── ¿Polyline vs Polygon? → intersección geométrica
    │       │   └── ¿Point vs Polygon? → punto dentro del polígono
    │       │
    │       ├── Si hay intersección:
    │       │   ├── Recortar geometría contra el corredor
    │       │   ├── Proyectar puntos extremos al eje
    │       │   │   └── axis.nearest_point(entry) → PK
    │       │   └── Crear LinearIntersection
    │       │
    │       └── Ordenar por entry_pk
    │
    └── 3. Devolver list[LinearIntersection]
```

## 3. Relaciones entre módulos

```
EPIC-001 (LRE)                    EPIC-002 (SQE)
┌─────────────────┐              ┌──────────────────────┐
│ Axis             │────────────→│ SpatialQueryEngine    │
│ Station          │────────────→│   (consume Axis,     │
│ PK               │             │    Station, Geometry) │
│ LateralProjection│────────────→│                      │
│ LinearEvent      │←────────────│   (produce           │
└─────────────────┘             │    LinearEvent)      │
                                 └──────────────────────┘
                                          │
                                  ┌───────┴───────┐
                                  │               │
                                  ▼               ▼
                        ┌──────────────┐  ┌──────────────┐
                        │ EPIC-003     │  │ EPIC-004     │
                        │ Municipios   │  │ Carreteras   │
                        └──────────────┘  └──────────────┘
```

## 4. Decisiones de diseño

| Decisión | Opción | Motivo |
|---|---|---|
| Estrategia de indexado | `dict[str, IndexedFeature]` (v1) | Simplicidad. R-tree vendrá si es necesario |
| Detección de intersección | Escaneo geométrico por segmento | Suficiente para el alcance actual |
| Ordenación de resultados | Por entry_pk ascendente | Coherente con el sistema de referenciación lineal |
| Formato de propiedades | `dict` genérico | Mantiene el SQE desacoplado de la semántica |
| Eventos de salida | `LinearEvent` del LRE | Reutiliza el modelo existente sin duplicar |
