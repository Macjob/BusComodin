# ADR 0005 — Política Connectivity-aware para M4

## Estado

Aceptado para M4.

## Decisión

M4 reutiliza exactamente el escenario, demanda, semillas, capacidad, métricas y pool persistente de tres buses comodín de M1-M3. La única dimensión nueva es la vulnerabilidad de conectividad.

La vulnerabilidad sintética de un paradero se define como la inversa del número de líneas regulares que lo sirven:

`vulnerabilidad = 1 / numero_de_lineas_regulares`

Así, un paradero con una sola alternativa recibe mayor prioridad que uno servido por dos o más líneas. Esta definición no intenta representar aún accesibilidad real; es un proxy reproducible para probar la hipótesis del proyecto sin introducir datos reales.

La puntuación M4 combina:

`score = pasajero-minutos de espera × 1.0 + exceso sobre capacidad × 8.0 + (vulnerabilidad × pasajeros esperando) × 120.0`

Los pesos y el modelo quedan congelados en `configs/policy-connectivity-aware-v1.json` y no se ajustan después de observar resultados.

## Resultado de referencia — seed 42

Con `synthetic-v1` y seed 42:

- baseline: espera media `6.2131 min`;
- queue-first: `5.8045 min`;
- dtpm-inspired: `6.2131 min`;
- wait-aware: `6.0901 min`;
- connectivity-aware: `5.7761 min`;
- connectivity-aware realiza 10 asignaciones y 201 minutos de reposicionamiento;
- las cinco políticas generan los mismos 808 pasajeros.

En esta seed, connectivity-aware obtiene la menor espera media de las políticas implementadas hasta M4, aunque la diferencia frente a queue-first es pequeña. Este resultado sigue siendo de una sola realización y no permite concluir superioridad general. La evaluación multi-seed corresponde a M5.

## Fuera de alcance

No se incorporan datos reales de cobertura, tiempos de caminata, frecuencias alternativas, Metro/tren, optimización de pesos ni experimentos multi-seed.
