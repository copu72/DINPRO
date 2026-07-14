# EPIC-002 — Spatial Query Engine (Plan de pruebas)

**Versión:** 0.1

---

## 1. Tests unitarios

| Módulo | Tests estimados | Cobertura objetivo |
|---|---|---|
| SpatialQueryEngine (indexado) | 15 | ≥95% |
| SpatialQueryEngine (consultas) | 25 | ≥95% |
| LinearIntersection | 5 | 100% |
| IndexedFeature | 3 | 100% |
| to_events | 8 | ≥95% |

**Total estimado:** 56 tests

## 2. Tests de integración

| Escenario | Descripción |
|---|---|
| Indexar geometrías de municipio, consultar contra eje | Validar flujo completo |
| Indexar geometrías de carretera, consultar contra corredor | Validar corredor |
| Consultar por rango de PK | Validar filtro por PK |
| Conversión a LinearEvents | Validar compatibilidad LRE |
| Limpiar y reindexar | Validar ciclo de vida |

## 3. Tests de propiedades

- `len(intersect_axis()) <= len(index())`
- `all(r.entry_pk <= r.exit_pk for r in results)`
- `all(r.affected_length >= 0 for r in results)`
- `results == sorted(results, key=lambda r: r.entry_pk)`
- `intersect_range(a, b) ⊆ intersect_axis()`
