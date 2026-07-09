# DINPRO

Plataforma de ingeniería y diseño de infraestructuras.

## Arquitectura

```
DINPRO
├── docs/      → Documentación del proyecto
├── specs/     → Especificaciones funcionales y técnicas
├── src/       → Código fuente (Core + Plugins + SDK)
├── tests/     → Pruebas
├── data/      → Datos oficiales y caché
├── resources/ → Iconos, temas, fuentes
├── examples/  → Proyectos de ejemplo
├── assets/    → Recursos gráficos del proyecto
├── devtools/  → Herramientas de desarrollo
├── sandbox/   → Prototipos y experimentos
├── installer/ → Instalador
└── scripts/   → Automatización
```

## Reglas de arquitectura

1. **El Core nunca cambia** — ninguna funcionalidad externa modifica `src/core/`.
2. **Nada entra en `src/` sin pasar por `specs/`** — primero se diseña, luego se implementa.
3. **Cada plugin es autocontenido** con su propio controller, services, models, repository, exporter y settings.

## Licencia

Ver archivo [LICENSE](LICENSE).
