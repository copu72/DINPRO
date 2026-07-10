# ADR-0006: Arquitectura en tres capas

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | El proyecto ha crecido y necesita una organización arquitectónica explícita. |

## Decisión
A partir de Sprint 3, DINPRO adopta una arquitectura en tres capas:

```
Presentación (GUI / CLI)       — Interfaz con el usuario
Servicios (Core + Plugins)     — Lógica de aplicación y negocio
Dominio (Geometry, CRS, Axis)  — Motor independiente y reutilizable
```

## Motivación
Separar la lógica de dominio (GSE) de los servicios y la presentación permite reutilizar el motor en otros contextos.

## Ventajas
- El dominio no depende de ninguna capa superior
- Los tests de dominio son puramente unitarios
- La API pública del dominio puede exponerse como librería independiente

## Inconvenientes
- Puede requerir más código de infraestructura (inyección de dependencias)
- Los desarrolladores deben respetar las direcciones de dependencia
