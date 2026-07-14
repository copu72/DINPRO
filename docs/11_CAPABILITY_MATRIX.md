# Capability Matrix

> Matriz de capacidades del producto DINPRO.
> Mide el progreso real no por código implementado, sino por funcionalidades completas que la plataforma ofrece.
> Versión: 0.3.1-dev

---

| Capacidad | Estado | EPICs relacionados | Depende de |
|---|---|---|---|
| **Geometría** (Point, Line, Polyline, Polygon, Circle, BBox) | ✅ Completo | GSE (Core) | — |
| **Sistemas de referencia** (CRS, UTM, ETRS89, WGS84) | ✅ Completo | GSE (Core) | Geometría |
| **Topología** (validación, auto-intersecciones, orientación) | ✅ Completo | GSE (Core) | Geometría |
| **Transformaciones** (pyproj, UTM-Krüger) | ✅ Completo | GSE (Core) | CRS |
| **Operaciones espaciales** (distancia, intersección, buffer) | ✅ Completo | GSE (Core) | Geometría |
| **Eje lineal** (Axis, PK, Station) | ✅ Completo | LRE (EPIC-001) | Geometría |
| **Referenciación lineal** (LinearReferencing) | ✅ Completo | LRE (EPIC-001) | Eje lineal |
| **Medida lineal** (MeasureSystem, calibraciones) | ✅ Completo | LRE (EPIC-001) | Referenciación lineal |
| **AdvancedStationing** (Station Value Object, parsing, formateo) | ✅ Completo | LRE (EPIC-001) | Medida lineal |
| **Proyección lateral** (offset, sección transversal, corredores) | ✅ Completo | LRE (EPIC-001) | Eje lineal |
| **Segmentación dinámica** (sub-ejes por rango de PK) | 🚧 En desarrollo | LRE (EPIC-001) | Proyección lateral |
| **Eventos lineales** (LinearEvent) | ⏳ Pendiente | LRE (EPIC-001) | Segmentación dinámica |
| **Calibración de ruta** (RouteCalibration) | ⏳ Pendiente | LRE (EPIC-001) | Medida lineal |
| **Perfil longitudinal** | ⏳ Pendiente | LRE (EPIC-001) | Eje lineal |
| **Exportación LRE** | ⏳ Pendiente | LRE (EPIC-001) | Eventos lineales |
| **Consultas espaciales** (SQE) | 📝 Diseño | SQE (EPIC-002) | LRE + Geometría |
| **Municipios** | ⏳ Pendiente | Módulo funcional | SQE |
| **Carreteras** | ⏳ Pendiente | Módulo funcional | SQE |
| **Hidrografía** | ⏳ Pendiente | Módulo funcional | SQE |
| **Catastro** | ⏳ Pendiente | Módulo funcional | SQE |
| **Infraestructuras** | ⏳ Pendiente | Módulo funcional | SQE |

---

## Leyenda

| Símbolo | Significado |
|---|---|
| ✅ Completo | Capacidad implementada, testeada, revisada y aprobada |
| 🚧 En desarrollo | Capacidad en implementación activa |
| 📝 Diseño | Especificación aprobada, implementación pendiente |
| ⏳ Pendiente | Capacidad identificada, no iniciada |

---

## Historial

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-07-14 | 0.3.1-dev | Creación inicial con 21 capacidades |
