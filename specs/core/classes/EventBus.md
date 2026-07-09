# EventBus

Sistema de eventos para comunicación desacoplada entre componentes.

## Responsabilidades

- Publicar eventos.
- Suscribir/desuscribir oyentes.
- Encolar eventos.
- Proveer tipado de eventos.

## API Pública

```python
class EventBus:
    def publish(self, event: str, data: dict | None = None) -> None
    def subscribe(self, event: str, callback: Callable) -> str  # returns subscription_id
    def unsubscribe(self, subscription_id: str) -> None
    def clear(self) -> None

    @property
    def subscribers_count(self) -> int

# Eventos predefinidos del sistema
EVENT_PROJECT_OPENED = "project.opened"
EVENT_PROJECT_SAVED = "project.saved"
EVENT_PROJECT_CLOSED = "project.closed"
EVENT_MODULE_LOADED = "module.loaded"
EVENT_MODULE_UNLOADED = "module.unloaded"
EVENT_MODULE_RUN_COMPLETED = "module.run.completed"
EVENT_ERROR = "system.error"
```

## Uso

```python
# Un módulo se suscribe a eventos
project.events.subscribe("project.opened", self.on_project_opened)

# Otro módulo publica
project.events.publish("module.run.completed", {"module": "carreteras", "status": "ok"})
```
