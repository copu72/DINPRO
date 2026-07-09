from dinpro.core.errors import (
    AxisError,
    ConfigurationError,
    DinproError,
    ExportError,
    GeometryError,
    ImportError,
    PluginError,
    PluginLoadError,
    PluginNotFoundError,
    ProjectError,
    ValidationError,
)


class TestErrors:
    def test_dinpro_error_base(self):
        assert issubclass(ProjectError, DinproError)
        assert issubclass(GeometryError, DinproError)
        assert issubclass(PluginError, DinproError)
        assert issubclass(ConfigurationError, DinproError)
        assert issubclass(AxisError, DinproError)
        assert issubclass(ImportError, DinproError)
        assert issubclass(ExportError, DinproError)
        assert issubclass(ValidationError, DinproError)

    def test_plugin_hierarchy(self):
        assert issubclass(PluginNotFoundError, PluginError)
        assert issubclass(PluginLoadError, PluginError)

    def test_error_message(self):
        try:
            raise GeometryError("Invalid geometry")
        except DinproError as e:
            assert str(e) == "Invalid geometry"
