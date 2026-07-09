# Secuencia de arranque

## Diagrama de secuencia

```
Usuario              Project              Logger        Settings     PluginManager    EventBus
  │                     │                    │              │              │             │
  │── project.start() ──▶                    │              │              │             │
  │                     │── initialize() ────▶              │              │             │
  │                     │                    │── OK ────────▶              │             │
  │                     │── load() ──────────────────────────▶              │             │
  │                     │                    │              │── OK ────────▶             │
  │                     │── scan() ────────────────────────────────────────▶             │
  │                     │                    │              │              │── OK ───────▶
  │                     │── start() ────────────────────────────────────────────────────▶
  │                     │                    │              │              │             │── OK
  │                     │◀───────────────────┼──────────────┼──────────────┼─────────────
  │◀──── "Core ready" ──┤                    │              │              │
```

## Salida esperada

```
DINPRO Professional
Version 0.1.0
────────────────────
Core initialized
Logger initialized
Configuration loaded
Workspace ready
Waiting modules...
```

## Código de arranque

```python
from dinpro import Project

project = Project()
project.start()
```
