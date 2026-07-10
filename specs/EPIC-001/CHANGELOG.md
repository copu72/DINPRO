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

### Sprint 4.4 — DynamicSegmentation

*Pendiente de implementar*

### Sprint 4.5 — LinearEvents

*Pendiente de implementar*

### Sprint 4.6 — RouteCalibration

*Pendiente de implementar*

### Sprint 4.7 — LongitudinalProfile

*Pendiente de implementar*

### Sprint 4.8 — Exporter

*Pendiente de implementar*

### Sprint 4.9 — Refactor + Tests + Benchmarks

*Pendiente de implementar*

---

**Sprint actual:** Ninguno (pendiente de inicio)
**Próximo Sprint:** 4.1 — MeasureSystem
