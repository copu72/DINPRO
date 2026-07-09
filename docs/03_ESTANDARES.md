# Estándares de DINPRO

## Código

- Python 3.10+.
- PEP 8 como referencia base.
- Tipado estático obligatorio (`mypy` strict mode).
- Nombres en inglés para código, en español para documentación.
- `snake_case` para variables y funciones. `PascalCase` para clases. `UPPER_CASE` para constantes.

## Commits

- Formato: `tipo(ámbito): descripción`
- Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Ejemplo: `feat(core/geometry): implementar cálculo de distancia entre puntos`
- Commits atómicos: un cambio por commit.

## Ramas

- `master` — estable, solo merge desde PR.
- `develop` — integración.
- `feature/*` — ramas de funcionalidad.
- `fix/*` — ramas de corrección.

## Pruebas

- Cobertura mínima: 80 %.
- `pytest` como framework.
- Pruebas unitarias obligatorias en cada módulo.
- Pruebas de integración para flujos completos.

## Documentación

- Docstrings en formato Google.
- README por cada módulo cuando sea necesario.
- `docs/` para documentación del proyecto.
- `CHANGELOG.md` mantenido manualmente siguiendo Keep a Changelog.
