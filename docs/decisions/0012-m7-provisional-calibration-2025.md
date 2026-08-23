# ADR 0012 — Calibración provisional UN11 2025

## Estado

Calibración histórica provisional completada para el benchmark UN11 2025. No representa la operación vigente de agosto de 2026.

## Corrección temporal

La investigación de vigencia determinó que el contrato asociado a C01/C02/C03 terminó el 31-01-2026 y que EFE Valparaíso comenzó a cubrir transitoriamente la zona el 02-02-2026. Por ello, el escenario documentado con programa UN11 se conserva explícitamente como benchmark histórico 2025 y no como `current-2026`.

## Demanda

La intensidad sintética de M7 inicial generaba ~1.500 pasajeros/hora y saturaba artificialmente la red. La calibración provisional reduce la tasa efectiva de punta de 0.20 a 0.10 pasajeros/paradero/minuto.

Anclas utilizadas:

- PMTP/SECTRA: 91.372 viajes en bus urbano durante punta mañana en Gran Valparaíso.
- Origen Quilpué: 14.329 viajes en bus en punta mañana.
- Origen Villa Alemana: 12.733 viajes.
- Viajes internos Quilpué/Villa Alemana en bus durante punta mañana: 16.772.
- Reportes públicos de enero de 2026 estimaban ~3.000–5.000 usuarios diarios afectados por la suspensión de C01/C02/C03.

La demanda sigue marcada como `historical-provisional`: aún no se ha ingerido la microdata EOD ni validaciones observadas por servicio.

## Tiempo de viaje

Se reduce el proxy global de 2 a 1 minuto por paradero/tramo. La decisión se apoya en tiempos EOD 2014 publicados:

- intra Villa Alemana: ~19:12 min;
- intra Quilpué: ~20:18 min;
- Quilpué -> Villa Alemana: ~31:30 min;
- Villa Alemana -> Quilpué: ~30:27 min.

Con 2 min/parada, los recorridos largos UN11 quedaban claramente sobredimensionados. `1 min/parada` sigue siendo un proxy; debe ser reemplazado por SUMO/tiempos por tramo cuando se materialice esa capa.

## Capacidad

La documentación oficial confirma una flota mínima UN11 de 27 buses, pero no se encontró una capacidad de pasajeros verificable para los vehículos adjudicados en los documentos accesibles revisados. Se mantiene 35 pasajeros como valor provisional y se ejecuta sensibilidad 30/35/40/50.

El ranking de políticas es prácticamente invariante entre 30 y 50 pasajeros, por lo que la conclusión relativa no depende del valor 35.

## Resultado multi-seed calibrado

20 semillas, escenario `villa-alemana-un11-2025-calibrated-v1`:

| Política | Espera media | Cambio vs baseline | Left-behind medio |
| --- | ---: | ---: | ---: |
| baseline | 11.1773 | — | 0.70 |
| queue-first | 10.9386 | -2.14% | 0.20 |
| dtpm-inspired | 11.1179 | -0.53% | 0.70 |
| wait-aware | 10.8515 | **-2.91%** | 0.20 |
| connectivity-aware | 11.2066 | +0.26% | 0.20 |

La calibración cambia el ranking respecto del escenario sobrecargado: `wait-aware` pasa a liderar y DTPM-inspired deja de ser la mejor política. Esto confirma que la calibración de demanda/tiempos es crítica antes de interpretar políticas.

## Sensibilidad de capacidad

Para capacidades 30, 35, 40 y 50:

- baseline se mantiene alrededor de 11.17 min;
- queue-first mejora ~2.1%;
- wait-aware mejora ~2.9%;
- dtpm-inspired mejora ~0.5%;
- connectivity-aware empeora ~0.3%.

Los left-behind desaparecen prácticamente desde capacidad 35–40 en adelante. La ocupación máxima media del baseline es ~0.95 con capacidad 30, ~0.85 con 35, ~0.75 con 40 y ~0.61 con 50.

## Interpretación

Esta versión es un benchmark mucho más plausible que M7 inicial, pero todavía no es una calibración operacional final. Las conclusiones permitidas son relativas entre políticas dentro de este escenario histórico. No corresponde afirmar un beneficio real de ~3% para Villa Alemana actual.

## Próximos pasos

1. Recuperar/microprocesar EOD para asignación OD por macrozona y franja.
2. Materializar SUMO para tiempos por tramo y reposicionamiento espacial.
3. Identificar capacidad real de flota o mantener sensibilidad documentada.
4. Reconstruir por separado el escenario transitorio 2026 (EFE + servicios paralelos) si se desea evaluar la operación vigente.
