# EPIC-001: Linear Referencing Engine

## ADR — Architecture Decision Records

---

### ADR-0101: MeasureSystem desacoplado

**Estado:** Aceptada

**Contexto:** El sistema de PK del GSE liga la medida directamente a la distancia geométrica, lo que impide calibraciones, discontinuidades y reinicios de kilometración.

**Decisión:** Crear `MeasureSystem` como objeto separado que encapsula la relación entre la medida lineal y la distancia geométrica. Por defecto medida == distancia. Mediante `CalibrationPoint` y `MeasureDiscontinuity` se pueden modelar casos reales.

**Consecuencias:** La misma geometría puede tener múltiples sistemas de medida. Añade complejidad pero es necesaria para casos reales de carreteras con PK no continuos.

---

### ADR-0102: Eventos versionados

**Estado:** Aceptada

**Contexto:** Los eventos lineales deben ser auditables. Cuando un análisis cambia, debe poder rastrearse qué versión de los datos se utilizó.

**Decisión:** Cada `LinearEvent` contiene `version` (entero autoincremental), `revision` (hash o timestamp), `created_at` y `updated_at`. `LinearEventSet.audit_trail()` permite consultar el historial completo.

**Consecuencias:** Los eventos ocupan más memoria pero la trazabilidad queda garantizada.

---

### ADR-0103: Implementación incremental

**Estado:** Aceptada

**Contexto:** El LRE tiene 8 submódulos. Implementar todo de una vez genera código de calidad desigual y dificulta la revisión.

**Decisión:** Dividir en 9 micro-sprints (4.1 a 4.9). Cada uno produce un submódulo completo con tests, pasa ruff y tiene cobertura ≥ 90 %. No se avanza al siguiente sin aprobación del arquitecto.

**Consecuencias:** El desarrollo es más lento al principio pero más rápido cuando el proyecto escala.

---

### ADR-0104: Cero dependencias externas

**Estado:** Aceptada

**Contexto:** El LRE debe funcionar en cualquier entorno Python sin requisitos de instalación complejos.

**Decisión:** Todas las operaciones del LRE usan solo stdlib. openpyxl para Excel es opcional (adapter pattern). Si no está, `to_excel()` lanza un error informativo.

**Consecuencias:** El LRE se puede instalar y probar en cualquier sistema con Python 3.10+.
