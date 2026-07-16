# Sprint 4.7 — LongitudinalProfile

## Análisis del Dominio

**Objetivo:** Identificar los conceptos y relaciones del dominio que son comunes a cualquier infraestructura lineal y que deben formar parte del modelo de DINPRO.

---

## 1. Objetivo y alcance

### ¿Qué es un perfil longitudinal?

Es la representación gráfica y analítica de la elevación del terreno (o de la rasante de una infraestructura) a lo largo de un eje lineal, proyectada sobre un plano vertical que contiene al eje.

### ¿Qué problemas de ingeniería resuelve?

| Problema | Descripción |
|----------|-------------|
| Diseño geométrico | Definir la rasante óptima que minimice movimiento de tierras |
| Replanteo | Materializar en obra los PK con su cota de proyecto |
| Movimiento de tierras | Calcular volúmenes de desmonte y terraplén |
| Drenaje | Determinar pendientes mínimas para evacuación de aguas |
| Explotación | Conocer pendientes para limitaciones de velocidad, consumo, desgaste |
| Seguridad | Identificar puntos con pendiente crítica |
| Mantenimiento | Planificar fresados, refuerzos, reposiciones |

### ¿Qué infraestructuras abarca?

| Infraestructura | Particularidad del perfil |
|-----------------|---------------------------|
| Carretera | Rasante por tramos rectos + acuerdos verticales (parábola) |
| Ferrocarril | Pendientes máximas muy restrictivas (< 2% alta velocidad) |
| Línea eléctrica | Perfil de torres: vanos, flechas, distancia al suelo |
| Tubería/conducción | Pendiente mínima para autolimpieza, presión |
| Canal | Pendiente constante por tramos, sección abierta |
| Ciclovía/sendero | Pendiente máxima accesible |
| Pista forestal | Adaptación al terreno, drenaje transversal |

El modelo de DINPRO no debe especializarse en ninguna de ellas. Cada infraestructura particulariza los valores umbral, no la estructura del perfil.

---

## 2. Fuentes de referencia

### Normativa

| Norma | Aportación |
|-------|------------|
| PG-3 (España) | Definiciones de rasante, acuerdo vertical, peralte |
| Norma 6.1-IC (España) | Trazado de carreteras: pendientes máximas, longitudes críticas |
| AASHTO Green Book (EE. UU.) | Diseño geométrico: stopping sight distance, critical length of grade |
| UNE-CEN/TR 16986 | Intercambio de datos de carreteras |

### Estándares de intercambio

| Formato | Aportación |
|---------|------------|
| LandXML | `Alignment/Profile` — `ProfAlign` con `PVI` (Point of Vertical Intersection), `ProfilePoint` con `station`, `elevation` |
| Civil 3D | `TinSurface` → perfil dinámico, `ProfileView` para presentación |
| IFC Alignment 1.1 | `IfcAlignment` con `IfcAlignmentVertical` — modelo BIM de infraestructuras |
| BGL (Alemania) | Estándar para intercambio de datos de carreteras |

### Práctica profesional

| Práctica | Aportación |
|----------|------------|
| Cubicación por secciones | El perfil longitudinal es la entrada para generar secciones transversales |
| Perfil de proyecto vs terreno | Se comparan dos perfiles: el del terreno natural y el de la rasante diseñada |
| Informe de pendientes | Tabla resumen con tramos de pendiente constante, desniveles acumulados |

---

## 3. Conceptos fundamentales del dominio

| Concepto | Definición | ¿Universal? |
|----------|------------|-------------|
| **Perfil longitudinal** | Secuencia ordenada de puntos (station, elevation) a lo largo de un eje | ✅ |
| **Rasante** | Línea que define la cota de proyecto (no la del terreno) | ✅ (concepto) |
| **Terreno** | Línea que define la cota del terreno natural | ✅ |
| **Estación (Station/PK)** | Posición sobre el eje, en unidades de longitud | ✅ |
| **Distancia** | Longitud geométrica acumulada desde el origen del eje | ✅ |
| **Elevación** | Cota del punto, en unidades de longitud (m) | ✅ |
| **Pendiente (Grade)** | Relación entre cambio de elevación y distancia horizontal | ✅ |
| **Cambio de rasante** | Punto donde cambia la pendiente (PVI — Point of Vertical Intersection) | ✅ |
| **Acuerdo vertical** | Curva vertical (parábola) que enlaza dos tramos de pendiente distinta | ✅ (carretera/FC) |
| **Punto singular** | Máximo, mínimo, inicio/fin de rampa, cambio de convexidad | ✅ |
| **Desnivel acumulado** | Suma de subidas y bajadas | ✅ |
| **Longitud desarrollada** | Longitud real sobre la superficie 3D (no la proyección horizontal) | ✅ |

---

## 4. Objetos del dominio (candidatos)

Sin decidir aún si serán Entity, Value Object o Domain Service:

| Candidato | Tipo probable | Razón |
|-----------|---------------|-------|
| `ProfilePoint` | Value Object (inmutable) | station + distance + elevation + grade + metadata |
| `GradeSegment` | Value Object (inmutable) | intervalo con pendiente constante |
| `ProfileStatistics` | Value Object | métricas: desniveles, pendientes medias, longitudes |
| `ElevationProvider` | Interface/Protocol | abstracción para obtener elevaciones |
| `ElevationSample` | Value Object | station + elevation (+ confidence, source) |
| `LongitudinalProfile` | Aggregate Root o Domain Service | opera sobre el perfil, genera análisis |
| `VerticalIntersection` | Value Object | PVI: station, elevation, grade_in, grade_out |

---

## 5. Casos de uso de ingeniería

### 5.1 Perfil del terreno

> Obtener la elevación del terreno natural a intervalos regulares (step) sobre un eje calibrado.

**Entrada:** `Axis` + `ElevationProvider` + `step` + (opcional) `Station` range  
**Salida:** `list[ProfilePoint]`

### 5.2 Perfil de rasante de proyecto

> Comparar perfil del terreno con perfil de proyecto.

**Entrada:** 2 perfiles (terreno, rasante)  
**Salida:** `list[(station, elevation_terrain, elevation_grade, difference)]`

### 5.3 Tramos de pendiente constante

> Agrupar el perfil en segmentos donde la pendiente es constante (± tolerancia).

**Entrada:** `list[ProfilePoint]` + `tolerance`  
**Salida:** `list[GradeSegment]`

### 5.4 Puntos singulares

> Detectar automáticamente puntos altos, bajos, cambios de pendiente, inicio/fin de rampa.

**Entrada:** `list[ProfilePoint]`  
**Salida:** `list[ProfilePoint]` con tipo de singularidad

### 5.5 Estadísticas del perfil

| Métrica | Cómo se calcula |
|---------|-----------------|
| Desnivel total | `elevation_last - elevation_first` |
| Desnivel positivo acumulado | Suma de diferencias positivas entre puntos consecutivos |
| Desnivel negativo acumulado | Suma de diferencias negativas (en valor absoluto) |
| Pendiente media | `desnivel_total / longitud_total` |
| Pendiente máxima | Máximo `abs(grade)` del perfil |
| Pendiente mínima | Mínimo `abs(grade)` del perfil |
| Longitud en subida | Suma de tramos con grade > 0 |
| Longitud en bajada | Suma de tramos con grade < 0 |
| Pendiente RMS | Raíz cuadrada de la media de `grade²` |
| % con pendiente > X% | Porcentaje de longitud con `abs(grade) > umbral` |

### 5.6 Perfil parcial

> Obtener el perfil de un `Segment` o rango de PK.

**Entrada:** `Segment` (o rango) + `ElevationProvider`  
**Salida:** `list[ProfilePoint]` (solo del rango)

### 5.7 Exportación

> El `Exporter` (Sprint 4.8) consumirá `list[ProfilePoint]` y `list[GradeSegment]` para generar CSV, GeoJSON, Excel.

---

## 6. Independencia del origen de datos

### Contrato del `ElevationProvider`

```python
class ElevationProvider(Protocol):
    def elevation_at(self, distance: float, station: Station) -> float | None: ...

    def sample_range(
        self,
        distance_start: float,
        distance_end: float,
        step: float,
    ) -> list[ElevationSample]: ...
```

**Decisiones arquitectónicas (propuesta):**

1. `ElevationProvider` no conoce Axis — solo consulta por distancia/station
2. `LongitudinalProfile` combina `Axis` + `ElevationProvider` + `RouteCalibration`
3. Las implementaciones concretas (MDT, LandXML, LiDAR, GNSS) se inyectan desde fuera del dominio
4. El dominio no depende de ningún formato — depende de la abstracción `ElevationProvider`

### ElevationSample

```python
@dataclass(frozen=True)
class ElevationSample:
    distance: float
    station: Station
    elevation: float
    confidence: float = 1.0
    source: str = "unknown"
```

---

## 7. Posibles obstáculos / preguntas abiertas

| Pregunta | Impacto |
|----------|---------|
| ¿Cómo manejar datos de elevación ausentes o incompletos? | `elevation_at` devuelve `None` → el perfil tiene huecos |
| ¿Cómo gestionar cambios bruscos de pendiente? | Tolerancia configurable para `slope_segments()` |
| ¿Debe el perfil soportar curvas verticales (acuerdos)? | Sí para carretera/FC, pero no bloquea el modelo base |
| ¿Cómo se relaciona con el futuro SQE? | El SQE podría consumir perfiles ya generados para consultas espaciales |
| ¿Debe `ProfilePoint.grade` calcularse al generar el punto o es una operación del perfil? | Propuesta: el punto guarda elevación; `grade` se deriva al procesar el perfil |

---

## 8. Conclusiones

### Conceptos consolidados

| Concepto | Incluir en modelo matemático |
|----------|------------------------------|
| ProfilePoint (station, distance, elevation, cumulative_length) | ✅ |
| GradeSegment (start, end, grade, length) | ✅ |
| ProfileStatistics (desniveles, pendientes, longitudes) | ✅ |
| ElevationProvider (interfaz abstracta) | ✅ |
| ElevationSample (station, elevation, confidence) | ✅ |
| Punto singular (tipo + punto) | ✅ |

### Requisitos para el modelo matemático (Fase 2)

1. **Muestreo:** Generar puntos de perfil a paso constante sobre el eje calibrado
2. **Interpolación de elevación:** Entre dos puntos de elevación conocida (lineal)
3. **Pendiente:** `grade = Δelevation / Δdistance` (tramo a tramo)
4. **Acumulados:** Suma incremental de distancia y desnivel
5. **Segmentación por pendiente:** Algoritmo de detección de tramos con pendiente constante (± tolerancia)
6. **Puntos singulares:** Detección de máximos, mínimos y cambios de convexidad en la serie de pendientes
7. **Estadísticos:** Fórmulas cerradas para todas las métricas (no requieren iteración adicional)

### Lo que NO incluye esta fase

| Excluido | Motivo |
|----------|--------|
| Curvas verticales (acuerdos parabólicos) | Se incorporan en una extensión; el modelo base trabaja con pendientes rectas |
| Suavizado de perfil | Operación de post-procesado, no del dominio central |
| Visualización | Pertenece a Presentation, no al dominio |
| Formatos de importación | Se resuelven mediante implementaciones de `ElevationProvider` |

---

*Documento preparado para la sesión de diseño del modelo matemático.*
