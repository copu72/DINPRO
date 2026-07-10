# EPIC-001 — Architecture Notes

> Decisiones de diseño específicas del EPIC que no justifican un ADR completo.
> Actualizado tras cada micro-sprint.

---

## Sprint 4.1 — MeasureSystem

### MeasureSystem como servicio del dominio

No es una utilidad ni una clase de datos. Es un servicio con estado que gestiona
la relación entre la geometría del eje y la medida lineal. Esto permite que
futuros submódulos (DynamicSegmentation, RouteCalibration) dependan de él como
intermediario sin acoplarse directamente a Geometry ni a Axis.

### Búsqueda O(log n) mediante `bisect`

Se optó por `bisect` sobre `dict` o `list` lineal porque:
- Las calibraciones están ordenadas por distancia
- Las inserciones/modificaciones son poco frecuentes (vs lecturas)
- `bisect` es nativo, sin dependencias, O(log n) por consulta
- Alternativas como `sortedcontainers` introducirían dependencia externa

### Excepciones del dominio (tarea diferida)

Actualmente se usa `ValueError` para PK negativas. Antes del cierre del EPIC-001
se migrará a una jerarquía propia:

```
DinproError
  └── LinearReferencingError
          ├── InvalidPKError
          ├── CalibrationError
          ├── MeasureSystemError
          └── DiscontinuityError
```

Ver `docs/adr/ADR-0006.md` como base para la jerarquía global.

### Inmutabilidad futura

`MeasureSystem` es actualmente mutable (`calibrate`, `add_discontinuity`, `clear`).
El objetivo a medio plazo es migrar a un modelo inmutable donde las operaciones
devuelvan nuevas instancias:

```python
new_ms = ms.with_calibration(...)
```

Beneficios: debugging, ausencia de efectos secundarios, concurrencia, tests robustos.

### MeasureReference (concepto futuro)

El modelo actual PK → Distancia es insuficiente para infraestructuras reales
donde existen:

- Cambios de kilometración
- Reinicios de PK (PK 0+000 tras PK 10+000)
- Múltiples sistemas de medida sobre el mismo eje

Se introducirá `MeasureReference` como capa intermedia entre PK y geometría:

```
PK → MeasureReference → Geometría
```

Esto permitirá representar discontinuidades y recalibraciones sin modificar
el eje. No se implementa en Sprint 4.1 pero queda como requisito de evolución.

---

## Sprint 4.2 — AdvancedStationing

### Station como Value Object

`Station` es un Value Object inmutable (`@dataclass(frozen=True)`). 
Implementa `__lt__`, `__le__`, `__gt__`, `__ge__`, `__eq__`, `__hash__` para 
comportarse como `datetime` o `Path`. La igualdad usa `math.isclose` con 
tolerancia 1e-9.

### Parsing sin expresiones regulares

`StationParser` usa una secuencia determinista:
1. Eliminar prefijo (PK, P.K., pk...)
2. Normalizar separador PK al canónico `+`
3. Detectar signo
4. Si hay separador PK: dividir en km + m
5. Si no: parsear como float

i18n: separador decimal (`.` o `,`), separador PK (`+`, `-`...), prefijo 
configurables desde el constructor. No se implementan todas las variantes, 
pero la API no las impide.

### Formateo por estrategia

`StationFormatter` es un ABC con 4 estrategias:
- `ClassicFormatter`: `15+345.20` (2 decimales por defecto)
- `DecimalFormatter`: `15345.200` (3 decimales)
- `EngineeringFormatter`: `15+345.200` (3 decimales en metros)
- `CustomFormatter`: configuración total (prefijo, separadores, decimales)

Cada formatter es independiente y testeable. No existe lógica de formateo 
fuera de los formatters.

### Tests de propiedades

Se incluyen tests de ida y vuelta:
- `parse(format(station)) == station.value`
- `format(parse(text))` produce representación canónica
- Reflexividad, simetría, transitividad de `==`, `<`, `>`
- Consistencia de `hash` con `==`

### Observaciones del Architect Review (v0.1)

1. **Representación canónica de Station**: `repr(station)` debe ser inequívoco
   (actualmente `Station(15345.235)`), mientras que `str(station)` usa el formatter
   por defecto del proyecto. Esto facilita debugging.

2. **StationParser stateless**: El parser ya es inmutable (configuración recibida en
   el constructor), pero debe garantizarse que no mantenga estado mutable. Es seguro
   para concurrencia.

3. **Formattable (futuro)**: Se introducirá una interfaz común `Formattable` con
   `obj.format(...)` para que `Station`, `Measure`, `PK`, `LinearEvent` compartan
   la misma filosofía de representación. Pendiente de implementar.

---

## Sprint 4.3 — LateralProjection

*Pendiente*

---

## Sprint 4.4 — DynamicSegmentation

*Pendiente*

---

## Sprint 4.5 — LinearEvents

*Pendiente*

---

## Sprint 4.6 — RouteCalibration

*Pendiente*

---

## Sprint 4.7 — LongitudinalProfile

*Pendiente*

---

## Sprint 4.8 — Exporter

*Pendiente*

---

## Sprint 4.9 — Integración + Benchmarks

*Pendiente*
