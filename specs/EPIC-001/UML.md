# EPIC-001: Linear Referencing Engine

## UML — Modelo de clases

---

### Diagrama de clases (relaciones principales)

```
┌─────────────────────────────────────────────────────────────┐
│                        Axis (GSE)                           │
├─────────────────────────────────────────────────────────────┤
│ +polyline: Polyline                                         │
│ +crs: CRS                                                   │
│ +measure_systems: list[MeasureSystem]                       │
│ +with_measure_system(ms) → Axis                             │
│ +length() → float                                           │
│ +point_at_pk(pk) → Point                                    │
│ +pk_at_point(point) → PK                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────────────────────┐
          │             │                            │
          ▼             ▼                            ▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────────┐
│ LateralProjection│ │ AdvancedStationing│ │ DynamicSegmentation  │
├─────────────────┤ ├──────────────────┤ ├─────────────────────┤
│ -axis: Axis     │ │ -axis: Axis      │ │ -axis: Axis         │
│ +offset_point() │ │ -measure_system  │ │ +split_by_events()  │
│ +cross_section()│ │ +point_at_pk()   │ │ +merge_segments()   │
│ +left() / right()│ │ +pk_at_point()   │ │ +clip()             │
└─────────────────┘ │ +format_pk()     │ │ +intersection()     │
                     └──────────────────┘ └─────────────────────┘
                              │
                              ▼
                     ┌──────────────────┐     ┌──────────────────────┐
                     │   MeasureSystem  │     │   RouteCalibration   │
                     ├──────────────────┤     ├──────────────────────┤
                     │ -calibrations[]  │     │ -axis: Axis          │
                     │ -discontinuities │     │ +auto_calibrate()    │
                     │ -direction       │     │ +adjust_pk()         │
                     │ +pk_at_distance()│     │ +reset_pk()          │
                     │ +distance_at_pk()│     │ +validate()          │
                     └──────────────────┘     └──────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                        LinearEvent                           │
├──────────────────────────────────────────────────────────────┤
│ -event_id: str (UUID)                                        │
│ -event_type: str                                             │
│ -pk_start: PK                                                │
│ -pk_end: PK                                                  │
│ -attributes: dict                                            │
│ -version: int                                                │
│ -revision: str (hash ISO 8601)                               │
│ -created_at: str                                             │
│ -updated_at: str                                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │    LinearEventSet     │
                     ├──────────────────────┤
                     │ -_events: dict        │
                     │ -_index               │
                     │ +add() / remove()     │
                     │ +update()             │
                     │ +query()              │
                     │ +query_range()        │
                     │ +overlaps()           │
                     │ +gaps()               │
                     │ +audit_trail()        │
                     └──────────────────────┘

┌────────────────────────────────────────────┐
│            LongitudinalProfile              │
├────────────────────────────────────────────┤
│ -axis: Axis                                │
│ +profile(step) → list[ProfilePoint]        │
│ +slope_segments(tol) → list[LinearSegment] │
│ +maximum_slope() → (PK, float)             │
│ +critical_points() → list[ProfilePoint]    │
│ +accumulated_climb() → float               │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│               LREExporter                   │
├────────────────────────────────────────────┤
│ -axis: Axis                                │
│ +to_csv(events, path)                      │
│ +to_geojson(events, path)                  │
│ +to_excel(events, path)                    │
└────────────────────────────────────────────┘
```

### Value Objects

```
PK(value: float)
├── from_string("PK 25+350") → PK
├── to_string() → str
├── to_station() → Station
└── +, -, <, >, ==, hash

Station(kilometers: int, meters: float)
├── total_meters → float
└── to_pk_string() → str

CalibrationPoint(pk: float, distance: float)

MeasureDiscontinuity(start_pk: float, end_pk: float, gap_before: float)

LinearSegment(pk_start: PK, pk_end: PK, length: float, attributes: dict)

ProfilePoint(pk: PK, elevation: float, slope: float, accumulated_length: float)
```
