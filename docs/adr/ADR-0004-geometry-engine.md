# ADR-0004: Geometry & Spatial Engine (GSE) como módulo de dominio

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO necesita un motor geométrico propio, sin depender de Shapely o GDAL directamente. |

## Decisión
Se crea `dinpro.domain` como capa de dominio independiente con: geometrías propias (Point, Line, Polyline, Polygon, Circle, BoundingBox), sistema CRS desacoplado, transformaciones espaciales, referenciación lineal (PK) y topología.

## Motivación
El motor geométrico es el componente más importante de DINPRO. Debe ser independiente de AutoCAD, Excel, GUI o cualquier fuente de datos.

## Ventajas
- Cero dependencias externas para operaciones básicas
- API estable para todos los módulos (Catastro, Carreteras, etc.)
- Adapter a Shapely/GDAL para operaciones complejas sin contaminar la API pública
- Tests unitarios rápidos (sin I/O, sin C extensions)

## Inconvenientes
- Mayor esfuerzo de implementación inicial
- Las operaciones complejas (buffer exacto, clip) pueden tener limitaciones sin Shapely

## Alternativas descartadas
- **Shapely directamente:** Rechazado porque crea dependencia forzada y la API de Shapely no está alineada con el dominio vial/español
- **GDAL vía CLI:** Rechazado por lentitud y dependencia externa
