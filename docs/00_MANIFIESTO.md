# DINPRO Manifiesto

## Propósito

DINPRO es una plataforma modular para el análisis, diseño y documentación técnica de infraestructuras lineales, desarrollada con estándares profesionales, basada en datos oficiales y preparada para evolucionar durante muchos años.

## Qué es DINPRO

- Una plataforma profesional de ingeniería lineal.
- Un sistema basado en plugins, donde cada módulo es independiente.
- Un proyecto diseñado para durar décadas.

## Qué pretende

- Estandarizar el flujo de trabajo en proyectos de infraestructura lineal.
- Centralizar datos oficiales (catastro, municipios, carreteras, ríos) en un entorno profesional.
- Permitir la extensión mediante plugins sin modificar el núcleo.
- Ser la referencia técnica en ingeniería lineal de código abierto.

## Qué nunca hará

- Depender de un solo formato o proveedor.
- Modificar el Core desde los módulos.
- Sacrificar calidad por velocidad.
- Acumular deuda técnica por prisas.

## Cómo se desarrolla

1. **FASE 0** — Documentación
2. **FASE 1** — Arquitectura
3. **FASE 2** — Core
4. **FASE 3** — Módulos
5. **FASE 4** — GUI
6. **FASE 5** — Pruebas
7. **FASE 6** — Instalador

No se saltan fases. No se improvisa.

## Calidad mínima

- Cada módulo tendrá especificación, implementación y pruebas.
- El Core no conocerá los módulos. Los módulos conocerán el Core.
- Nada entra en `src/` sin haber pasado por `docs/`.
- Todo commit debe ser atómico y descriptivo.

## Para la IA que contribuya

- No generar código sin haber definido antes la arquitectura.
- Señalar decisiones de diseño antes de implementar.
- Priorizar claridad sobre complejidad.
- No asumir nada: preguntar si hay duda.

## Para el desarrollador humano

- La arquitectura manda sobre la implementación.
- Un módulo bien diseñado hoy evitará reescribirlo mañana.
- La plataforma es más importante que cualquier funcionalidad concreta.

---

*Este manifiesto es la constitución de DINPRO. No se modifica sin consenso.*
