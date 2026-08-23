# ADR 0003 — Política DTPM-inspired para M2

## Estado

Aceptado para M2.

## Fuente y parámetros

M2 toma como benchmark los antecedentes documentados en `docs/precedents/chile-santiago.md`. Los parámetros quedan congelados en `configs/policy-dtpm-inspired-v1.json`:

- intervalo anormal: mayor que el máximo entre `headway programado + 15 min` y `2 × headway programado`;
- aglomeración: cola superior a `1.2 × capacidad del bus`;
- servicio corto predefinido inicial: `L2`, desde `S08` hasta `S16`.

Estos valores no se ajustan después de observar resultados de la simulación.

## Decisión

La política reutiliza exactamente el pool persistente de tres buses comodín de M1. Un vehículo disponible solo se asigna si existe al menos un servicio que cumple un gatillo de intervalo o aglomeración. El reposicionamiento sigue pagando tiempo físico sobre el grafo sintético.

Cuando el punto gatillado pertenece a un servicio corto predefinido, el comodín termina en el final de ese tramo y vuelve a quedar disponible desde allí. En caso contrario continúa hasta el terminal de la línea.

Los headways usados por el gatillo se calculan únicamente con buses regulares; una inyección no redefine el intervalo programado de la línea.

## Resultado de referencia — seed 42

Con `synthetic-v1` y seed 42:

- baseline: espera media `6.2131 min`;
- queue-first: espera media `5.8045 min`;
- dtpm-inspired: espera media `6.2131 min`;
- dtpm-inspired realiza 3 asignaciones y 27 minutos de reposicionamiento;
- no se activa el servicio corto en esta realización.

Que M2 no mejore M0 en esta seed es un resultado válido. El escenario M0 tiene operación regular sin perturbaciones, por lo que los gatillos históricos tienen pocas oportunidades de intervenir. No se relajarán los umbrales para fabricar una mejora. Escenarios con congestión o fallos parciales corresponden a experimentos posteriores del roadmap.

## Fuera de alcance

No se incorpora espera acumulada como prioridad, vulnerabilidad de conectividad, optimización de parámetros, datos reales ni perturbaciones artificiales del escenario base.
