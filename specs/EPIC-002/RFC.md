# EPIC-002 — Spatial Query Engine (SQE)

**Estado:** RFC
**Versión:** 0.1
**Depende de:** EPIC-001 (LRE) — Axis, Station, LateralProjection
**Habilita:** EPIC-003 (Municipios), EPIC-004 (Carreteras), EPIC-005 (Hidrografía), EPIC-006 (Catastro)

---

## 1. Problema

DINPRO necesita responder preguntas espaciales referenciadas al eje lineal:

- ¿Qué entidades (municipios, carreteras, ríos, parcelas) intersectan este eje?
- ¿En qué PK entran y salen?
- ¿Qué longitud del eje resulta afectada?
- ¿Qué eventos lineales genera cada intersección?

Hoy estas preguntas se responderían con código ad-hoc en cada módulo, duplicando lógica espacial y de referenciación lineal.

## 2. Solución propuesta

Un **Spatial Query Engine (SQE)** que:

1. **Indexa** geometrías externas (municipios, carreteras, etc.) junto con metadatos.
2. **Consulta** contra un eje (o corredor) y devuelve intersecciones referenciadas a PK.
3. **Genera** eventos lineales a partir de los resultados.
4. **Ignora** la semántica de las entidades — trabaja solo con geometrías y metadatos.

## 3. Principios de diseño

| Principio | Descripción |
|---|---|
| **Sin acoplamiento semántico** | El SQE no conoce Municipios, Carreteras ni ningún dominio específico. Solo geometrías + metadatos. |
| **Orientado al eje** | Todas las consultas se referencian al sistema lineal del proyecto (PK, Station, Axis). |
| **Incremental** | La primera versión puede implementar escaneo lineal simple. Un R-tree real vendrá después si el rendimiento lo exige. |
| **Componible** | Los resultados del SQE se alimentan directamente a LinearEvents. |
| **Sin dependencias externas** | Usa la geometría nativa de DINPRO (Point, Polyline, Polygon) y el LRE. |

## 4. Casos de uso

| CU | Descripción | Prioridad |
|---|---|---|
| CU-01 | Indexar un conjunto de geometrías externas | Alta |
| CU-02 | Consultar intersecciones con el eje (PK inicial, PK final) | Alta |
| CU-03 | Consultar intersecciones con un corredor (eje ± half_width) | Alta |
| CU-04 | Consultar intersecciones en un rango de PK | Alta |
| CU-05 | Obtener el PK de entrada/salida de una geometría dada | Media |
| CU-06 | Obtener la longitud afectada de cada intersección | Alta |
| CU-07 | Generar eventos lineales a partir de intersecciones | Alta |
| CU-08 | Limpiar y reindexar | Media |

## 5. Relación con el LRE

```
LRE (EPIC-001)
  │
  ├── Axis ──────────→ SQE: input geométrico
  ├── Station ───────→ SQE: resultado referenciado
  ├── LateralProjection → SQE: consulta por corredor
  │
  └── LinearEvents ←── SQE: salida como eventos
```

El SQE consume objetos del LRE y produce datos que el LRE puede representar como eventos lineales.

## 6. No alcance (para esta versión)

- Implementación de R-tree u otro índice espacial avanzado (se hará si el rendimiento lo requiere).
- Persistencia de índices entre sesiones.
- Consultas puramente geométricas sin referencia a eje (ej: "¿qué geometrías están a menos de 500 m de este punto?").
- Operaciones topológicas avanzadas (unión, intersección entre geometrías externas).

## 7. Criterios de aceptación

| CA | Descripción |
|---|---|
| CA-01 | Indexar N geometrías y recuperarlas mediante consulta |
| CA-02 | Consulta contra eje devuelve intersecciones ordenadas por PK |
| CA-03 | Consulta contra corredor devuelve intersecciones dentro del ancho |
| CA-04 | Consulta por rango de PK devuelve solo intersecciones en ese rango |
| CA-05 | Cada intersección contiene entry_pk, exit_pk, affected_length |
| CA-06 | SQE no conoce tipos de entidades (solo geometría + metadatos) |
| CA-07 | Rendimiento lineal respecto al número de geometrías indexadas |
| CA-08 | Sin dependencias externas de geometría espacial |
