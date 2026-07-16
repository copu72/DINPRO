# EPIC-001: Linear Referencing Engine

## CHANGELOG

---

### 2026-07-10 — v0.1 (RFC)

- Creación de la RFC del LRE
- Aprobada por Architect Review
- Se identifican 8 submódulos y 9 micro-sprints

### 2026-07-10 — v1.0 (SPEC)

- SPEC funcional completa
- API pública definida
- Casos de uso documentados (8)
- Criterios de aceptación establecidos
- Plan de pruebas benchmark objetivos definidos

### Sprint 4.1 — MeasureSystem

- Implementado `MeasureSystem` como servicio del dominio
- `CalibrationPoint` y `MeasureDiscontinuity` como dataclasses
- Soporte para: calibraciones, discontinuidades, interpolación lineal
- `pk_at_distance` / `distance_at_pk` bidireccionales
- `validate()` con detección de desviación >1%
- 24 tests, ruff clean, mypy clean, 96% cobertura
- Pendiente de Architect Review

### Sprint 4.2 — AdvancedStationing

- Implementado `Station` como Value Object inmutable, comparable, hasheable, ordenable
- `StationParser` determinista sin expresiones regulares
- `StationFormatter` con 4 estrategias: Classic, Decimal, Engineering, Custom
- i18n desde diseño: separador decimal, separador PK, prefijo configurables
- Parsing robusto: `15+345.20`, `PK 15+345`, `pk15+345`, `15 + 345`, `15+345,20`
- 100 tests, ruff clean, mypy clean, 99-100% cobertura en módulos core
- Tests de propiedades: roundtrip parse(format(x))==x, hash, comparaciones
- Pendiente de Architect Review

### Sprint 4.3 — LateralProjection

*Pendiente de implementar*

### Sprint 4.5 — LinearEvents

- `EventType`, `EventSource`, `EventStatus` como Enums del dominio
- `EventMetadata` separado del evento (DA-009)
- `EventReference` para conectar entidades externas
- `LinearEvent` como Value Object inmutable con `axis` + `segment` (sin geometría propia — DA-005)
- `LinearEventSet` como Aggregate Root (DA-007): add, update, remove, filter, sort, merge, split, group_by, query_range, overlaps, gaps, audit_trail, statistics
- 158 tests, cobertura 94-100%, ruff/mypy clean
- **Architect Implementation Review:** 🟢 APPROVED (commit 8f25a70)
- 5 decisiones DA-005 a DA-009 registradas en ARCHITECT_NOTES

### Sprint 4.4 — DynamicSegmentation

- Implementado `Segment` como Value Object inmutable del dominio
- `DynamicSegmentation` como servicio: segment(), split(), merge()
- `Segment` con: reverse(), contains(), intersects(), clip(), offset(), to_axis()
- `_extract_subpolyline()` para extraer subtramos del eje
- 46 tests, ruff clean, mypy clean, cobertura 94-97%
- **Architect Review:** 🟢 APPROVED (commit d47a15f)
- Correcciones aplicadas: `Segment.id` estable, `offset()` sin parámetro `side`, `reverse()` documentado
- **Tag:** `v0.4.0-sprint-4.4`

### Sprint 4.5 — LinearEvents

*Pendiente de implementar*

### Sprint 4.6 — RouteCalibration

- RFC + SPEC aprobadas (Architect Review 🟢 APPROVED)
- Decisiones D-13 a D-18, DA-010, DA-011 registradas
- Modelo matemático: piecewise linear, f(d) y f⁻¹(s), O(log n) + O(1)
- Implementado: CalibrationPoint, CalibrationSet, ExtrapolationMode, CalibrationIssue, RouteCalibration
- 53 tests, coverage 90%+, ruff/mypy clean
- **Architect Implementation Review:** 🟢 APPROVED (commit 560ae80)

### Sprint 4.7 — LongitudinalProfile

*Pendiente de implementar*

### Sprint 4.8 — Exporter

*Pendiente de implementar*

### Sprint 4.9 — Refactor + Tests + Benchmarks

*Pendiente de implementar*

---

**Sprint actual:** 4.7 — LongitudinalProfile (pendiente)
**Último completado:** 4.6 — RouteCalibration 🟢 APPROVED
