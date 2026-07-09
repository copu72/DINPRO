# API Architecture

```
                ┌─────────────────────────────┐
                │          Project             │
                │  (objeto único del programa) │
                └────────────┬────────────────┘
                             │
            ┌────────────────┼────────────────┬──────────────────┐
            ▼                ▼                ▼                  ▼
     ┌──────────┐    ┌────────────┐   ┌───────────┐    ┌──────────────┐
     │ Settings │    │   Axis     │   │ Geometry  │    │   Results    │
     └──────────┘    └────────────┘   └───────────┘    └──────────────┘
                                                     ┌────────────────┐
                                                     │  PluginManager │
                                                     └────────────────┘
                                                     ┌────────────────┐
                                                     │   EventBus     │
                                                     └────────────────┘
                                                     ┌────────────────┐
                                                     │    Logger      │
                                                     └────────────────┘
```

## Flujo de arranque

```
1. Project.start()
2.   ├── Logger.initialize()
3.   ├── Settings.load()
4.   ├── PluginManager.scan()
5.   ├── EventBus.start()
6.   └── Project ready → "Waiting modules..."
```

## Flujo de un módulo

```
1. PluginManager.load("carreteras")
2.   ├── Busca módulo en plugins/
3.   ├── Verifica que hereda de Module
4.   ├── module.initialize()
5.   └── Module registrado en EventBus

6. module.run()
7. module.validate()
8. module.export()
9. module.cleanup()
```
