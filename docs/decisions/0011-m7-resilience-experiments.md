# ADR 0011 — Experimentos de resiliencia sobre UN11 real-network

## Estado

Ejecutado como experimento técnico de M7 sobre la red/oferta UN11 ya materializada. La demanda, capacidad y tiempos siguen parcialmente modelados, por lo que los resultados no deben interpretarse como impacto operacional real.

## Diseño

Se congeló `configs/scenario-villa-alemana-real-am-v1.json` y se aplicaron perturbaciones simples de oferta duplicando el headway de servicios seleccionados:

- normal;
- C01 a 50% de oferta;
- C02 a 50%;
- C03 a 50%;
- C04 a 50%;
- C01 y C02 simultáneamente a 50%.

Cada caso se ejecutó con 20 semillas y cinco políticas: baseline, queue-first, dtpm-inspired, wait-aware y connectivity-aware. Total: 600 corridas.

## Resultados destacados

| Perturbación | Baseline espera media | Mejor política | Espera media mejor | Mejora |
| --- | ---: | --- | ---: | ---: |
| normal | 27.2641 | dtpm-inspired | 26.6106 | 2.40% |
| C01 half-service | 29.0204 | dtpm-inspired | 28.0348 | 3.40% |
| C02 half-service | 28.7408 | queue-first | 28.2857 | 1.58% |
| C03 half-service | 27.9865 | dtpm-inspired | 27.3205 | 2.38% |
| C04 half-service | 26.4933 | dtpm-inspired | 25.7601 | 2.77% |
| C01+C02 half-service | 30.7441 | queue-first | 30.2003 | 1.77% |

## Patrones observados

`dtpm-inspired` es la política más consistente en este escenario: mejora frente a baseline en normal, C01, C02, C03 y C04, aunque en la perturbación conjunta C01+C02 queda igual que baseline. `queue-first` ayuda en C01/C02/C03 y en la perturbación conjunta, pero empeora en C04. `connectivity-aware` produce mejoras pequeñas y estables en la mayoría de los casos. `wait-aware` empeora de forma consistente frente a baseline bajo estas condiciones.

La mejor mejora observada es 3.40% en C01 half-service con dtpm-inspired. Esto es bastante menor que las mejoras de 10–20% observadas en M5 sintético bajo fallos parciales, lo que indica que la estructura de UN11 y/o la demanda provisional cambian significativamente el espacio de decisión.

## Interpretación metodológica

No se recalibró ninguna política tras observar estos resultados. La demanda sintética mantiene saturación alta y los tiempos de recorrido siguen representados con 2 minutos por parada, por lo que estas cifras deben leerse como comportamiento relativo del algoritmo bajo una red más realista, no como estimación de beneficio real en Villa Alemana/Quilpué.

## Reproducibilidad

`tools/run_m7_resilience.py` ejecuta las 600 corridas y escribe:

- `outputs/m7-resilience/runs.json`
- `outputs/m7-resilience/summary.json`

## Próximo paso

Antes de nuevas conclusiones sobre resiliencia se debe calibrar demanda, capacidad y tiempos de viaje. Luego se repetirá exactamente este mismo runner para medir cuánto cambia la señal con los parámetros calibrados.
