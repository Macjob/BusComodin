# ADR 0006 — Experimentos multi-seed M5

## Diseño

M5 congela 20 semillas y ejecuta las cinco políticas sobre el mismo escenario por caso. Se varían de forma aislada demanda, capacidad, headways, tiempo de viaje (proxy de congestión), fallo parcial de una línea (duplicación de su headway) y número de buses comodín. No se ajustan políticas ni pesos a partir de estos resultados.

El runner produce datos crudos CSV y un resumen JSON con media e intervalo normal aproximado del 95% para la espera media.

## Resultado base — 20 semillas

- baseline: 5.9575 min (IC95 5.8838–6.0312)
- queue-first: 5.6505 min (5.5651–5.7359), mejora media ~5.2%
- wait-aware: 5.6566 min (5.5585–5.7547), mejora media ~5.1%
- connectivity-aware: 5.6644 min (5.5764–5.7524), mejora media ~4.9%
- dtpm-inspired: 5.9509 min (5.8766–6.0253), prácticamente baseline

La ventaja observada en seed 42 no se conserva exactamente: en el agregado base queue-first queda levemente primero, y las tres políticas adaptativas principales quedan muy próximas.

## Perturbaciones destacadas

Los comodines muestran más valor cuando la red se degrada. Ante fallo parcial de L1, baseline sube a 9.1177 min y connectivity-aware baja a 7.9515 min (~12.8% menos). Ante fallo parcial de L3, baseline es 8.6969 min, queue-first 7.0910 y wait-aware 7.0172 (~19.3% menos que baseline para wait-aware).

Con capacidad al 75%, baseline es 6.2069 min frente a 5.8128 wait-aware y 5.8160 connectivity-aware (~6.3% menos).

## Buses marginales

En el escenario base aparece rendimiento decreciente muy rápido: pasar de 1 a 2 buses mejora, pero 2–5 buses producen prácticamente la misma espera media en estas políticas. Esto sugiere que el benchmark base no genera suficientes crisis simultáneas para aprovechar más de dos comodines; no debe interpretarse como un óptimo operacional real.

## Limitaciones

El proxy de congestión redondea tiempos de viaje enteros, por lo que multiplicadores 1.25 y 1.5 sobre 3 minutos pueden colapsar al mismo valor. El fallo parcial es un proxy simple (headway duplicado), no una interrupción espacial real. M6/M7 deberán reemplazar estos proxies con red y operación más realistas.
