# EPIC-001: Linear Referencing Engine (LRE)

## RFC — Request For Comments

**Estado:** Aprobada
**Autor:** Arquitecto Jefe
**Versión:** 1.0

---

### Resumen

El LRE extiende el sistema de PK básico del GSE para convertirlo en un motor completo de referenciación lineal con estacionamiento avanzado, eventos lineales, segmentación dinámica, proyecciones laterales, calibración de rutas, perfil longitudinal y sistema de medidas desacoplado de la geometría.

### Motivación

Todos los módulos funcionales (Municipios, Carreteras, Hidrografía, Infraestructuras, Catastro) necesitan responder preguntas sobre PK, intersecciones y tramos. Sin un motor común, cada módulo duplicaría esa lógica.

### Dependencias

- GSE v0.3.0 (Geometry, CRS, LinearReferencing, Axis)
- Solo stdlib de Python

### Decisiones arquitectónicas

1. **MeasureSystem**: Separar la medida lineal de la geometría del eje para soportar calibración, discontinuidades y reinicios de kilometración.
2. **Event versioning**: Cada LinearEvent lleva `version`, `revision`, `created_at`, `updated_at` para auditoría y reproducibilidad.
3. **Implementación incremental**: 9 micro-sprints, cada uno con SPEC → UML → API → Tests → Code Review → Merge.

### Micro-sprints planificados

| Sprint | Módulo | Esfuerzo estimado |
|--------|--------|-------------------|
| 4.1 | MeasureSystem | 3 días |
| 4.2 | AdvancedStationing | 2 días |
| 4.3 | LateralProjection | 2 días |
| 4.4 | DynamicSegmentation | 3 días |
| 4.5 | LinearEvents | 4 días |
| 4.6 | RouteCalibration | 3 días |
| 4.7 | LongitudinalProfile | 2 días |
| 4.8 | Exporter | 2 días |
| 4.9 | Refactor + Tests + Benchmarks | 3 días |

### Riesgos identificados

| Riesgo | Mitigación |
|--------|------------|
| Calibración imprecisa con pocos puntos | Validación con error > 1% |
| Rendimiento con > 10000 eventos | Índice interno en LinearEventSet |
| Complejidad del MeasureSystem | Empezar con sistema directo, calibración en iteración posterior |
