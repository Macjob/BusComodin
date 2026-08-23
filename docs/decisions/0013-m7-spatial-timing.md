# ADR 0013 — Tiempos espaciales provisionales M7

## Estado

Aceptado como referencia espacial provisional hasta materializar SUMO.

## Motivación

El benchmark calibrado UN11-2025 todavía usaba un tiempo homogéneo de 1 minuto por parada. Ese proxy no representa diferencias de longitud entre recorridos ni permite un reposicionamiento temporalmente ponderado.

## Evidencia externa

El Plan Maestro de Transporte Público del Gran Valparaíso de SECTRA reporta una velocidad promedio de buses cercana a 30 km/h en punta mañana. Se usa ese valor como ancla de velocidad comercial de sistema, no como velocidad observada específica de C01/C02/C03/C03Y/C04.

## Construcción

`tools/spatialize_m7_2025.py` parte del escenario calibrado 2025 y del matching OSM sobre shapes oficiales DTPR. Para reducir el exceso de puntos OSM y mantener resolución temporal entera:

1. muestrea aproximadamente un punto representativo por minuto comercial (~500 m a 30 km/h);
2. deriva tiempos enteros por tramo desde la distancia acumulada sobre el shape;
3. conserva las frecuencias oficiales del Anexo N°3;
4. escala la tasa base por la razón de paradas antiguas/nuevas para conservar aproximadamente la intensidad total del benchmark y aislar el cambio de topología/tiempos.

Resultado: 79 paradas únicas representativas y tiempos por tramo explícitos en `scenario-villa-alemana-un11-2025-spatial-v1.json`.

## Cambio del motor

`Line` admite ahora `segment_travel_minutes` opcional. Escenarios anteriores siguen usando `Scenario.travel_time_minutes` como fallback. El reposicionamiento de comodines usa Dijkstra sobre tiempos de tramo en vez de contar saltos.

También se corrigió el cierre de la ventana: se programa la expedición regular en `t = duration_minutes`, permitiendo que pasajeros que llegan al final de la ventana tengan el siguiente bus, como ocurriría en una operación continua.

## Corrección de métricas

Se añadieron:

- `unserved_passengers`;
- `service_rate_pct`;
- `mean_censored_wait_minutes`;
- `p95_censored_wait_minutes`.

Para pasajeros no abordados, la espera censurada se cuenta hasta el final del horizonte de simulación. Esto evita que una política parezca mejor simplemente por no atender a pasajeros difíciles.

## Resultado normal — 20 seeds

Todos los pasajeros son atendidos en el escenario normal.

| Política | Espera media | Mejora vs baseline |
| --- | ---: | ---: |
| baseline | 10.4141 | — |
| queue-first | 10.0468 | 3.53% |
| dtpm-inspired | 10.4120 | 0.02% |
| wait-aware | 10.1371 | 2.66% |
| connectivity-aware | 10.1016 | 3.00% |

## Resiliencia espacial

En degradaciones simples, queue-first y connectivity-aware son generalmente competitivas. El caso más fuerte es C04 al 50% de oferta. Baseline deja una pequeña fracción sin servicio dentro del horizonte, por lo que la comparación principal usa espera censurada:

- queue-first: ~14.97% de mejora censurada;
- wait-aware: ~16.07%;
- connectivity-aware: ~13.80%;
- dtpm-inspired: ~0.01%.

En C01+C02 simultáneamente al 50%, connectivity-aware mejora ~4.35% en espera censurada y queue-first ~4.04%.

## Limitaciones

- Las paradas siguen siendo OSM secundario, no listado oficial UN11.
- La velocidad de 30 km/h es una media histórica del sistema.
- C01 tiene cobertura OSM incompleta frente a los kilómetros oficiales, por lo que su longitud proyectada queda subestimada.
- No se modelan semáforos, intersecciones, congestión por tramo ni dwell time explícito.
- SUMO sigue siendo el reemplazo previsto para esta capa.

## Conclusión

La señal de beneficio vuelve a aparecer de forma moderada en operación normal (~3%) y más fuerte bajo ciertas degradaciones (~15–16% censurado en C04). Estos valores siguen siendo resultados de un benchmark histórico/provisional, no predicciones actuales para Villa Alemana 2026.
