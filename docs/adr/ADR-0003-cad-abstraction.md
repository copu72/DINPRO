# ADR-0003: CAD Abstraction Layer (CAL)

| Campo | Valor |
|-------|-------|
| **Fecha** | 2025-01-20 |
| **Estado** | Aceptada |
| **Contexto** | DINPRO debe leer datos de AutoCAD (DWG), DXF y potencialmente otros formatos CAD. |

## Decisión
Se crea una capa de abstracción CAD (`dinpro.cad`) con una interfaz común (`CADAdapter`) y adaptadores concretos para DXF y AutoCAD.

## Motivación
Aislar al resto del programa del formato de origen. Si en el futuro se necesita soporte para BricsCAD o NanoCAD, solo se añade un adaptador.

## Ventajas
- El Core y los módulos nunca manipulan DXF/AutoCAD directamente
- Tests con DXF de prueba (sin necesidad de AutoCAD)
- El adaptador de AutoCAD solo se carga si está disponible

## Inconvenientes
- El adaptador de AutoCAD requiere COM (solo Windows)
- La abstracción añade una capa de indirección
