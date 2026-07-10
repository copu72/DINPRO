# Architecture Decision Record (ADR) — DINPRO

**Propósito:** Registrar todas las decisiones de arquitectura significativas, su motivación, ventajas, inconvenientes y alternativas descartadas.

---

## ADR-0001 — Arquitectura de plugins

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-15 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO necesita soportar múltiples dominios (carreteras, catastro, hidrografía, municipios) sin acoplar el núcleo a ninguno. |

### Decisión
Se adopta una arquitectura basada en plugins. El Core descubre y carga módulos desde `src/dinpro/plugins/` mediante el `PluginManager`.

### Motivación
- Separación total entre el núcleo y los módulos de negocio.
- Los plugins pueden desarrollarse en paralelo.
- Posibilidad de que terceros desarrollen plugins sin modificar el Core.

### Ventajas
- Bajo acoplamiento.
- Escalabilidad horizontal (nuevos dominios = nuevos plugins).
- Carga dinámica sin modificar el Core.

### Inconvenientes
- Mayor complejidad en la gestión de dependencias entre plugins.
- El mecanismo de descubrimiento requiere convenciones de nomenclatura.

### Alternativas descartadas
- **Módulos monolíticos:** Rechazado por falta de escalabilidad.
- **Microservicios:** Rechazado por sobreingeniería para una aplicación de escritorio.

---

## ADR-0002 — Inversión de dependencias (Core no conoce módulos)

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-15 |
| **Estado** | Aceptada |
| **Contexto** | El Core debe ser independiente de cualquier módulo de negocio o fuente de datos externa. |

### Decisión
El Core (Application, Project, EventBus, Settings) no importa ni conoce ningún módulo. Los módulos se comunican con el Core a través de interfaces definidas en el Core.

### Motivación
Cualquier cambio en un módulo no debe afectar al Core. Esto permite pruebas unitarias del Core sin dependencias externas.

### Ventajas
- Core testeable de forma aislada (100% stdlib).
- Los módulos pueden reimplementarse sin tocar el Core.
- Facilita la creación de la API pública.

### Inconvenientes
- Requiere definir interfaces con antelación.
- Mayor número de archivos.

---

## ADR-0003 — CAD Abstraction Layer (CAL)

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-20 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO debe leer datos de AutoCAD (DWG), DXF y potencialmente otros formatos CAD. |

### Decisión
Se crea una capa de abstracción CAD (`dinpro.cad`) con una interfaz común (`CADAdapter`) y adaptadores concretos para DXF y AutoCAD.

### Motivación
Aislar al resto del programa del formato de origen. Si en el futuro se necesita soporte para BricsCAD o NanoCAD, solo se añade un adaptador.

### Ventajas
- El Core y los módulos nunca manipulan DXF/AutoCAD directamente.
- Tests con DXF de prueba (sin necesidad de AutoCAD).
- El adaptador de AutoCAD solo se carga si está disponible.

### Inconvenientes
- El adaptador de AutoCAD requiere COM (solo Windows).
- La abstracción añade una capa de indirección.

---

## ADR-0004 — Formato .din para persistencia

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-25 |
| **Estado** | Aceptada |
| **Contexto** | Los proyectos de DINPRO deben guardarse y cargarse con todo su estado. |

### Decisión
Se crea el formato `.din` (JSON con secciones versionadas). Cada módulo es responsable de serializar/deserializar su estado.

### Motivación
Formato legible por humanos, fácil de depurar, sin dependencias binarias. El versionado permite compatibilidad hacia atrás.

### Ventajas
- Depurable con cualquier editor de texto.
- Compatible con control de versiones (Git diff).
- Cada módulo controla su serialización.

### Inconvenientes
- JSON no es eficiente para grandes volúmenes de datos.
- No soporta binarios (se requiere base64 para datos CAD incrustados).

---

## ADR-0005 — Geometry & Spatial Engine (GSE) como módulo de dominio

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO necesita un motor geométrico propio, sin depender de Shapely o GDAL directamente. |

### Decisión
Se crea `dinpro.domain` como capa de dominio independiente con: geometrías propias (Point, Line, Polyline, Polygon, Circle, BoundingBox), sistema CRS desacoplado, transformaciones espaciales, referenciación lineal (PK) y topología.

### Motivación
- El motor geométrico es el componente más importante de DINPRO.
- Debe ser independiente de AutoCAD, Excel, GUI o cualquier fuente de datos.
- Puede reutilizarse en una API pública futura.

### Ventajas
- Cero dependencias externas para operaciones básicas.
- API estable para todos los módulos (Catastro, Carreteras, etc.).
- Adapter a Shapely/GDAL para operaciones complejas sin contaminar la API pública.
- Tests unitarios rápidos (sin I/O, sin C extensions).

### Inconvenientes
- Mayor esfuerzo de implementación inicial.
- Las operaciones complejas (buffer exacto, clip) pueden tener limitaciones sin Shapely.

### Alternativas descartadas
- **Shapely directamente:** Rechazado porque crea dependencia forzada y la API de Shapely no está alineada con el dominio vial/español (PK, ejes, UTM).
- **GDAL vía CLI:** Rechazado por lentitud y dependencia externa.

---

## ADR-0006 — Arquitectura en tres capas

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | El proyecto ha crecido y necesita una organización arquitectónica explícita. |

### Decisión
A partir de Sprint 3, DINPRO adopta una arquitectura en tres capas:

```
┌──────────────────────────────┐
│ Presentación (GUI / CLI)     │  — Interfaz con el usuario
├──────────────────────────────┤
│ Servicios (Core + Plugins)   │  — Lógica de aplicación y negocio
├──────────────────────────────┤
│ Dominio (Geometry, Axis, CRS)│  — Motor independiente y reutilizable
└──────────────────────────────┘
```

### Motivación
Separar la lógica de dominio (GSE) de los servicios y la presentación permite reutilizar el motor en otros contextos.

### Ventajas
- El dominio no depende de ninguna capa superior.
- Los tests de dominio son puramente unitarios.
- La API pública del dominio puede exponerse como librería independiente.

### Inconvenientes
- Puede requerir más código de infraestructura (inyección de dependencias).
- Los desarrolladores deben respetar las direcciones de dependencia.

---

## ADR-0007 — Control de calidad por Sprint

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto | Es necesario garantizar que cada entrega cumple un estándar mínimo. |

### Decisión
Cada Sprint sigue el flujo:

```
SPEC → DESIGN REVIEW → IMPLEMENTATION → UNIT TESTS → ARCHITECT REVIEW → RELEASE
```

Si una fase no se supera, no se continúa a la siguiente.

### Motivación
- Evitar deuda técnica acumulada.
- Garantizar que cada versión es potencialmente publicable.
- Mantener la cobertura ≥ 90% en módulos críticos.

### Ventajas
- Calidad predecible y medible.
- El Architect Review detecta problemas antes de la release.
- La documentación se genera durante el proceso, no al final.

### Inconvenientes
- Ralentiza la entrega inicial.
- Requiere disciplina del equipo.

---

## ADR-0008 — Versiones LTS y nomenclatura

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | Es necesario comunicar la madurez de cada versión a los usuarios y desarrolladores de plugins. |

### Decisión

| Versión | Tipo |
|---------|------|
| 0.3.x | Desarrollo |
| 0.5.x | Beta |
| 0.9.x | RC |
| 1.0 | Estable |
| 1.2 | LTS |

### Motivación
- Los desarrolladores de plugins saben cuándo pueden esperar estabilidad.
- Los usuarios saben qué versiones son de referencia.
- Permite planificar la hoja de ruta con hitos claros.

### Ventajas
- Comunicación clara del estado del proyecto.
- Las versiones LTS reciben soporte prolongado.
- Las versiones de desarrollo permiten iterar rápido.

### Inconvenientes
- Requiere mantener ramas para versiones LTS.
- Aumenta la carga de mantenimiento.
