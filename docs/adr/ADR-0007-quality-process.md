# ADR-0007: Control de calidad por Sprint

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-02-09 |
| **Estado** | Aceptada |
| **Contexto** | Es necesario garantizar que cada entrega cumple un estándar mínimo. |

## Decisión
Cada Sprint sigue el flujo: RFC → SPEC Funcional → SPEC Técnica → Diseño UML → API Pública → Casos de prueba → Implementación → Code Review → Tests → Release.

Si una fase no se supera, no se continúa a la siguiente.

## Motivación
- Evitar deuda técnica acumulada
- Garantizar que cada versión es potencialmente publicable
- Mantener la cobertura ≥ 90% en módulos críticos

## Ventajas
- Calidad predecible y medible
- El Architect Review detecta problemas antes de la release
- La documentación se genera durante el proceso, no al final

## Inconvenientes
- Ralentiza la entrega inicial
- Requiere disciplina del equipo
