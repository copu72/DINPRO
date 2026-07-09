class DinproError(Exception):
    """Base exception for all DINPRO errors."""


class ProjectError(DinproError):
    """Raised when a project operation fails."""


class AxisError(DinproError):
    """Raised when an axis operation fails."""


class GeometryError(DinproError):
    """Raised when a geometry operation fails."""


class ConfigurationError(DinproError):
    """Raised when configuration loading or validation fails."""


class PluginError(DinproError):
    """Raised when a plugin operation fails."""


class PluginNotFoundError(PluginError):
    """Raised when a plugin is not found."""


class PluginLoadError(PluginError):
    """Raised when a plugin cannot be loaded."""


class ImportError(DinproError):
    """Raised when an import operation fails."""


class ExportError(DinproError):
    """Raised when an export operation fails."""


class ValidationError(DinproError):
    """Raised when validation fails."""
