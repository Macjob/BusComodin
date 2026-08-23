# ADR 0010 — Primera comparación multi-seed sobre UN11 real-network

## Estado

Ejecutado como baseline técnico de M7 antes de calibración final de demanda/capacidad/tiempos.

## Diseño

Se ejecutaron 20 semillas sobre `configs/scenario-villa-alemana-real-am-v1.json`, comparando baseline, queue-first, dtpm-inspired, wait-aware y connectivity-aware con exactamente la misma demanda por seed.

La red y frecuencias provienen de DTPR UN11. Las paradas son OSM map-matched. La demanda sigue siendo sintética no calibrada, la capacidad es provisional (35) y el tiempo de viaje es modelado (2 min/parada).

## Resultado

| Política | Espera media | IC95 aprox. | Cambio vs baseline |
| --- | ---: | ---: | ---: |
| baseline | 27.2641 | 26.9198–27.6085 | — |
| queue-first | 26.8580 | 26.3561–27.3599 | -1.49% |
| dtpm-inspired | 26.6106 | 26.1652–27.0560 | -2.40% |
| wait-aware | 27.5117 | 26.9970–28.0264 | +0.91% |
| connectivity-aware | 26.9561 | 26.6366–27.2755 | -1.13% |

En promedio, baseline registra 316.45 eventos left-behind y 1,459.9 pasajeros abordados; todas las políticas operan bajo saturación alta.

## Interpretación

La señal es pequeña y no debe tratarse como impacto operacional real. El escenario está dominado por una demanda sintética excesiva y por tiempos/capacidad provisionales. La diferencia de ranking frente a M5 sintético confirma que las políticas son sensibles a la estructura del escenario y que no corresponde optimizarlas antes de calibrar M7.

## Reproducibilidad

`tools/run_m7_multiseed.py` ejecuta las mismas 20 semillas usadas en M5 y escribe `outputs/m7-multiseed/runs.json` y `summary.json`.

## Próximo paso

Congelar primero:
1. demanda histórica calibrada desde EOD SECTRA;
2. capacidad/tipología de flota UN11;
3. tiempos de recorrido derivados de SUMO/OSM o fuente operacional.

Solo después repetir este runner y usar ese resultado para evaluar políticas.
