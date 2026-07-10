# ADR-0005: Formato .din para persistencia

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-25 |
| **Estado** | Aceptada |
| **Contexto** | Los proyectos de DINPRO deben guardarse y cargarse con todo su estado. |

## Decisión
Se crea el formato `.din` (JSON con secciones versionadas). Cada módulo es responsable de serializar/deserializar su estado.

## Motivación
Formato legible por humanos, fácil de depurar, sin dependencias binarias. El versionado permite compatibilidad hacia atrás.

## Ventajas
- Depurable con cualquier editor de texto
- Compatible con control de versiones (Git diff)
- Cada módulo controla su serialización

## Inconvenientes
- JSON no es eficiente para grandes volúmenes de datos
- No soporta binarios (se requiere base64 para datos CAD incrustados)
