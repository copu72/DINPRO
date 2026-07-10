# EPIC-001: Linear Referencing Engine

## BENCHMARK — Objetivos de rendimiento

---

### Objetivos medibles

| Operación | Objetivo | Condiciones |
|-----------|----------|-------------|
| point_at_pk sin calibración | < 1 ms | 1000 vértices, eje de 50 km |
| point_at_pk con calibración | < 2 ms | 10 puntos de calibración |
| pk_at_point | < 10 ms | 1000 vértices |
| nearest_pk | < 10 ms | 1000 vértices |
| offset_point (único) | < 1 ms | — |
| offset_points (100 pts) | < 50 ms | step=20, 2 km de eje |
| cross_section | < 1 ms | — |
| split_by_events (100 eventos) | < 100 ms | segmentación completa |
| merge_segments (100 segmentos) | < 50 ms | — |
| clip (rango 10 km) | < 10 ms | 1000 vértices |
| query (PK concreto) | < 1 ms | 1000 eventos |
| query_range (10 km) | < 5 ms | 1000 eventos |
| overlaps | < 100 ms | 1000 eventos |
| auto_calibrate (10 pts) | < 100 ms | — |
| validate_calibration | < 10 ms | — |
| profile (1000 pts, step=50) | < 500 ms | eje 50 km |
| slope_segments | < 100 ms | 1000 pts de perfil |
| to_csv (1000 eventos) | < 200 ms | — |
| to_geojson (1000 eventos) | < 500 ms | — |

### Entorno de referencia

- Python 3.13+
- Windows 11 / Linux
- CPU: cualquier x86_64 de los últimos 5 años
- RAM: 8 GB+
- SSD

### Almacenamiento de resultados

Los benchmarks se almacenan en `docs/benchmarks/lre/` con formato JSON:

```json
{
  "version": "0.4.0",
  "date": "2026-07-10",
  "environment": {
    "python": "3.13.7",
    "os": "Windows 11",
    "cpu": "AMD64"
  },
  "results": {
    "point_at_pk_ms": 0.45,
    "pk_at_point_ms": 3.2,
    "profile_ms": 280.0
  }
}
```
