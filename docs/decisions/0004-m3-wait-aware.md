# ADR 0004 — Política Wait-aware para M3

## Estado

Aceptado para M3.

## Decisión

M3 reutiliza exactamente el escenario, demanda, semillas, capacidad, métricas y pool persistente de tres buses comodín de M1/M2. La única dimensión nueva es la regla de prioridad.

La política puntúa cada combinación línea/paradero usando:

`score = pasajero-minutos de espera × 1.0 + exceso sobre capacidad × 8.0`

Los pesos quedan congelados en `configs/policy-wait-aware-v1.json` y no se ajustan después de observar resultados. La carga de espera se calcula como la suma de los minutos que llevan esperando los pasajeros de esa línea en ese paradero. El término de capacidad solo aparece cuando la cola supera la capacidad nominal del bus.

El refuerzo seleccionado se reposiciona físicamente igual que en M1 y recorre el servicio predefinido de la línea hasta su terminal. M3 no introduce servicios cortos propios ni información de conectividad.

## Resultado de referencia — seed 42

Con `synthetic-v1` y seed 42:

- baseline: espera media `6.2131 min`;
- queue-first: `5.8045 min`;
- dtpm-inspired: `6.2131 min`;
- wait-aware: `6.0901 min`;
- wait-aware realiza 11 asignaciones y 240 minutos de reposicionamiento;
- las cuatro políticas generan los mismos 808 pasajeros.

En esta única semilla, wait-aware mejora levemente al baseline pero queda por detrás de queue-first. Esto no se interpreta como superioridad o inferioridad general; la evaluación multi-seed corresponde a M5.

## Fuera de alcance

No se incorpora vulnerabilidad de conectividad, datos reales, optimización de pesos ni perturbaciones artificiales del escenario base.
