# Roadmap

## M0 — Baseline sintético reproducible

Objetivo: disponer de una simulación base sin buses comodín, determinista por semilla y con métricas comparables.

Entregables:
- paquete Python instalable;
- CLI `python -m buscomodin simulate baseline --seed 42`;
- escenario sintético (20–30 paraderos, 3 líneas, 2 hubs);
- demanda sintética variable;
- capacidad limitada por bus;
- resultados JSON/CSV;
- métricas: espera media, P95, left-behind, ocupación, headways;
- tests con pytest;
- notebook `notebooks/01_baseline.ipynb` consumiendo el mismo core.

## M1 — Queue-first

Objetivo: incorporar 3 buses comodín y una política simple que prioriza la mayor acumulación.

Comparar contra M0 usando exactamente el mismo escenario y semilla.

## M2 — DTPM-inspired

Objetivo: implementar una política inspirada en antecedentes de Santiago:
- refuerzo ante intervalos amplios;
- gatillos por saturación/aglomeración;
- posibilidad de servicio corto predefinido.

Los parámetros deben quedar explícitos y versionados.

## M3 — Wait-aware

Objetivo: priorizar no solo tamaño de cola, sino también tiempo acumulado de espera y riesgo de dejar pasajeros abajo.

## M4 — Connectivity-aware

Objetivo: agregar vulnerabilidad de conectividad.

Una cola menor puede tener mayor prioridad si el sector posee pocas alternativas de transporte o depende de una única línea.

## M5 — Experimentos

Ejecutar múltiples semillas y variaciones de:
- demanda;
- capacidad;
- número de comodines;
- headways;
- congestión;
- fallos parciales de líneas.

Resultados esperados:
- medias e intervalos de variación;
- comparación de políticas;
- análisis de mejora marginal por bus adicional.

## M6 — Escenario Villa Alemana simplificado

Importar red vial y nodos relevantes desde OpenStreetMap/SUMO, manteniendo demanda sintética al inicio.

No intentar todavía calibración completa con datos reales.

## M7 — Datos reales y calibración

Solo después de demostrar valor en escenarios sintéticos y simplificados:
- paraderos y trazados reales;
- frecuencias observadas;
- capacidad aproximada;
- conexiones a hubs/Metro;
- demanda real cuando exista una fuente adecuada.

## Regla metodológica

Ninguna política puede modificar métricas, semillas o escenarios para mejorar artificialmente su resultado. Toda comparación debe ejecutar exactamente el mismo escenario base salvo por la política de despacho bajo prueba.
