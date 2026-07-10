# EPIC-001: Linear Referencing Engine

## TEST_PLAN — Plan de pruebas

---

### Nivel 1: Unitarias (objetivo: 200+ tests)

| Módulo | Tests mínimos | Cobertura objetivo |
|--------|---------------|-------------------|
| MeasureSystem | 20 | ≥ 95 % |
| AdvancedStationing | 15 | ≥ 95 % |
| LateralProjection | 20 | ≥ 90 % |
| DynamicSegmentation | 25 | ≥ 90 % |
| LinearEvent / LinearEventSet | 30 | ≥ 95 % |
| RouteCalibration | 20 | ≥ 90 % |
| LongitudinalProfile | 15 | ≥ 90 % |
| LREExporter | 15 | ≥ 85 % |

### Nivel 2: Integración

- Axis + AdvancedStationing: point_at_pk(pk_at_point(x)) == x
- MeasureSystem + RouteCalibration: calibración consistente
- DynamicSegmentation + LinearEventSet: split produce segmentos correctos
- LateralProjection + SpatialOperations: offset_point + distance = distancia esperada

### Nivel 3: Regresión

- Conjunto de ejes de referencia en `tests/domain/data/lre/`
- Resultados esperados para cada operación
- Comparación automática en cada build

### Casos límite

- Eje con 2 vértices (mínimo)
- PK fuera de rango (antes del inicio, después del final)
- Calibración con 0 puntos
- Eventos con pk_start == pk_end
- Eventos solapados exactamente
- Perfil con elevación constante (pendiente 0)
- Exportación con 0 eventos

### Benchmarks

| Operación | Objetivo | Cómo se mide |
|-----------|----------|-------------|
| point_at_pk (calibrado) | < 2 ms | timeit 1000 iteraciones |
| pk_at_point | < 10 ms | timeit 1000 iteraciones |
| offset_points (100 pts) | < 50 ms | timeit 100 iteraciones |
| query_range (1000 eventos) | < 50 ms | timeit 100 iteraciones |
| profile (1000 pts) | < 500 ms | timeit 10 iteraciones |
