# ADR-0002: Inversión de dependencias (Core no conoce módulos)

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-15 |
| **Estado** | Aceptada |
| **Contexto** | El Core debe ser independiente de cualquier módulo de negocio o fuente de datos externa. |

## Decisión
El Core (Application, Project, EventBus, Settings) no importa ni conoce ningún módulo. Los módulos se comunican con el Core a través de interfaces definidas en el Core.

## Motivación
Cualquier cambio en un módulo no debe afectar al Core. Esto permite pruebas unitarias del Core sin dependencias externas.

## Ventajas
- Core testeable de forma aislada (100% stdlib)
- Los módulos pueden reimplementarse sin tocar el Core
- Facilita la creación de la API pública

## Inconvenientes
- Requiere definir interfaces con antelación
- Mayor número de archivos
