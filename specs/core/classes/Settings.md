# Settings

Configuración global y preferencias de usuario.

## Responsabilidades

- Cargar configuración desde archivo (JSON, TOML, YAML).
- Proveer valores con defaults.
- Validar tipos y rangos.
- Persistir cambios.

## API Pública

```python
class Settings:
    def load(self, path: str | None = None) -> None
    def save(self) -> None
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def reset(self, key: str) -> None
    def reset_all(self) -> None
    def as_dict(self) -> dict
    def validate(self) -> list[str]

    # Acceso tipado
    @property
    def language(self) -> str
    @property
    def units(self) -> str          # "metric" | "imperial"
    @property
    def crs_default(self) -> str    # "EPSG:25830"
    @property
    def log_level(self) -> str      # "DEBUG" | "INFO" | "WARNING" | "ERROR"
    @property
    def plugins_enabled(self) -> list[str]  # Lista de plugins activos
```

## Almacenamiento

- Archivo de configuración: `~/.dinpro/settings.toml` (usuario) y `./dinpro.toml` (proyecto).
- El archivo local sobreescribe al global.
