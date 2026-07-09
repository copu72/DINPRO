# DINPRO

**Plataforma modular para el análisis, diseño y documentación técnica de infraestructuras lineales.**

Basada en datos oficiales, construida con estándares profesionales, preparada para evolucionar durante años.

## Filosofía

- **Plugin-based**: el Core no conoce los módulos. Los módulos conocen el Core.
- **Specs first**: nada entra en `src/` sin pasar por `docs/`.
- **Fases estrictas**: no se salta ninguna fase del desarrollo.

## Estructura

```
DINPRO
├── .github/     → CI/CD y plantillas
├── docs/        → Manifiesto, visión, arquitectura, estándares
├── src/         → Código fuente (Core + Plugins + SDK)
├── tests/       → Pruebas
├── data/        → Datos oficiales y caché
├── tools/       → Herramientas de desarrollo
├── resources/   → Iconos, temas, fuentes
├── examples/    → Proyectos de ejemplo
├── assets/      → Recursos gráficos del proyecto
├── scripts/     → Automatización
└── specs/       → Casos de uso, diagramas, interfaces
```

## Documentación fundacional

- [00_MANIFIESTO.md](docs/00_MANIFIESTO.md) — Constitución del proyecto
- [01_VISION.md](docs/01_VISION.md) — Visión y principios
- [02_ARQUITECTURA.md](docs/02_ARQUITECTURA.md) — Arquitectura y reglas
- [03_ESTANDARES.md](docs/03_ESTANDARES.md) — Estándares de código
- [04_REGLAS_IA.md](docs/04_REGLAS_IA.md) — Reglas para IA contribuyente
- [05_ROADMAP.md](docs/05_ROADMAP.md) — Hoja de ruta

## Licencia

[MIT](LICENSE)
