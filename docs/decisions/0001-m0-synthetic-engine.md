# ADR 0001 — Motor sintético desacoplado para M0

## Estado

Aceptado para M0.

## Contexto

M0 debe validar de extremo a extremo un baseline fijo, reproducible y comparable antes de incorporar buses comodín o datos reales. El roadmap prefiere SUMO, pero explícitamente permite un motor sintético Python si integrar SUMO bloquea el primer milestone.

## Decisión

Implementar M0 con un motor discreto y determinista en Python estándar. El escenario vive en `configs/scenario-v1.json`; demanda, simulación, métricas y persistencia son módulos separados. El notebook consume el mismo API público `load_scenario` + `run_baseline` y no duplica lógica.

Los pasajeros eligen una línea disponible en su origen y un destino posterior dentro de esa línea. La demanda cambia durante una ventana de hora punta. Los buses regulares salen con headways fijos, capacidad finita y tiempo de viaje fijo entre paraderos.

`passengers_left_behind` cuenta pasajeros únicos que, al menos una vez, no pudieron abordar un bus elegible por falta de capacidad. Las métricas de espera se calculan sobre pasajeros que alcanzan a abordar durante la simulación.

## Consecuencias

- M0 no depende de SUMO ni de binarios externos.
- La semilla controla únicamente la realización de demanda y permite comparaciones futuras sobre la misma muestra.
- El escenario queda versionado y no se ajustará después de observar resultados para favorecer políticas futuras.
- Una futura integración SUMO/TraCI puede reemplazar el backend de movimiento manteniendo generación de demanda, métricas y orquestación separadas.
- No se implementa ninguna política de refuerzo en este milestone.
