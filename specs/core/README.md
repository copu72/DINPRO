# Core — Especificación de arquitectura

## Propósito

El Core es el corazón de DINPRO. Todo pasa por él. No sabe nada de carreteras, catastro, Excel ni municipios. Solo conoce geometría y gestión de proyectos.

## Principios

- **El Core es una API.** Los módulos hablan con él, nunca entre ellos.
- **Inversión de dependencias.** Core no conoce módulos. Los módulos conocen el Core.
- **Objeto único `Project`.** Todo vive dentro de Project. No hay variables globales.
- **Diseñado para v10.0.** Cada decisión de diseño mira a 10 años.

## Diagrama de dependencias

```
GUI
 │
 ├── Módulo Carreteras
 ├── Módulo Catastro
 ├── Módulo Excel
 ├── Módulo Municipios
 └── ...
         │
         ▼
      CORE  ←  SDK (Module base class)
         │
         ▼
    Geometry
```

Los módulos se comunican exclusivamente a través del Core. Prohibido: `carreteras.get_excel()`.

## Componentes del Core

| Componente     | Responsabilidad                                  |
|---------------|--------------------------------------------------|
| Project       | Contenedor único del proyecto activo             |
| Axis          | Eje: lectura, PK, interpolación, vértices       |
| Geometry      | Operaciones espaciales básicas                   |
| Results       | Contenedor de resultados de módulos              |
| Settings      | Configuración global y preferencias de usuario   |
| Logger        | Registro de toda la actividad                    |
| PluginManager | Carga, descarga, ejecución de módulos            |
| EventBus      | Comunicación desacoplada entre componentes       |
| Errors        | Gestión centralizada de errores                  |
