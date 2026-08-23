# Cierre de sesión — 2026-08-23

## Estado alcanzado
BusComodin ya tiene un benchmark histórico/provisional sobre UN11 2025 de Quilpué/Villa Alemana con trazados DTPR C01/C02/C03/C03Y/C04, frecuencias oficiales, paradas OSM map-matched, demanda histórica provisional, tiempos espaciales por tramo, reposicionamiento por menor tiempo y métricas de espera censurada. Escenario de referencia: `configs/scenario-villa-alemana-un11-2025-spatial-v1.json`.

## Hipótesis
> Una pequeña flota de buses de refuerzo que opere normalmente y pueda reasignarse dinámicamente hacia servicios degradados puede reducir desproporcionadamente el costo de una disrupción —especialmente la espera— sin mantener esa capacidad extra fija en cada recorrido.

Debe evaluarse contra una alternativa con la misma cantidad total de buses para aislar el valor de la flexibilidad.

## Evidencia provisional
Operación normal (20 seeds): baseline 10.4141 min; queue-first 10.0468 (-3.53%); connectivity-aware 10.1016 (-3.00%); wait-aware 10.1371 (-2.66%); dtpm-inspired 10.4120 (-0.02%).

C04 al 50%, espera censurada: wait-aware ~16.07% mejor; queue-first ~14.97%; connectivity-aware ~13.80%; dtpm-inspired ~0.01%.

## Próximo experimento prioritario
Comparar con igualdad estricta de flota: baseline vs N buses adicionales asignados permanentemente (`fixed-extra`) vs los mismos N buses reasignables (`flexible-extra`), N=1..5, mismas seeds, operación normal y perturbaciones. Medir espera media/censurada, P95, tasa de servicio, left-behind, utilización y reposicionamiento.

Criterio principal: si `flexible-extra` supera robustamente a `fixed-extra` con la misma flota, hay evidencia de valor atribuible a la flexibilidad.

## Pendientes
- materializar SUMO para sustituir tiempos provisionales;
- mejorar cobertura C01;
- localizar paradas oficiales modernas si aparecen;
- capacidad exacta sigue como incertidumbre secundaria;
- reconstruir por separado la operación vigente 2026: UN11-2025 es benchmark histórico.

## Reproducibilidad
Runners: `tools/run_m7_multiseed.py`, `tools/run_m7_resilience.py`, `tools/run_m7_capacity_sensitivity.py`, `tools/spatialize_m7_2025.py`.

Decisiones: `docs/decisions/0012-m7-provisional-calibration-2025.md`, `docs/decisions/0013-m7-spatial-timing.md`. PR de trabajo: #16 (`m7-real-data`).
