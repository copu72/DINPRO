# ADR-0001: Arquitectura de plugins

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-15 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO debe soportar múltiples dominios (carreteras, catastro, hidrografía, municipios) sin acoplar el núcleo a ninguno. |

## Decisión
Se adopta una arquitectura basada en plugins. El Core descubre y carga módulos desde `src/dinpro/plugins/` mediante el `PluginManager`.

## Motivación
Separación total entre el núcleo y los módulos de negocio. Los plugins pueden desarrollarse en paralelo.

## Ventajas
- Bajo acoplamiento
- Escalabilidad horizontal (nuevos dominios = nuevos plugins)
- Carga dinámica sin modificar el Core

## Inconvenientes
- Mayor complejidad en la gestión de dependencias entre plugins
- El mecanismo de descubrimiento requiere convenciones de nomenclatura

## Alternativas descartadas
- **Módulos monolíticos:** Rechazado por falta de escalabilidad
- **Microservicios:** Rechazado por sobreingeniería para una aplicación de escritorio
