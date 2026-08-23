# ADR 0009 — M7 simulation-ready: red y oferta UN11 reales

## Estado

M7 queda listo para iniciar simulaciones sobre una red/oferta realista, pero no queda completamente calibrado. Se distingue explícitamente entre datos oficiales, datos secundarios y parámetros aún modelados.

## Red operacional materializada

Fuente oficial: DTPR `DSL4654 - UN11`, publicada 22-10-2024.

Se materializó el KMZ `documentoId=21963290` con SHA-256:

`80ae9c17994b65f727415e18f3a91487ab0fdc328c54bbfc150b61bff55e3994`

Contiene diez shapes: ida/regreso de C01, C02, C03, C03Y y C04. El contrato aprobado mediante Decreto Exento N°792/2025 confirma que estos cinco servicios componen UN11 y comenzaron a operar el 01-02-2025.

## Oferta programada

Se materializaron las Bases DTPR (`documentoId=21963165`), SHA-256:

`82df5d6bb176572f0480f7a13af71658ef6ee6c6fab353f4e1b35d79767a9163`

El Anexo N°3 contiene el Programa de Operación, incluyendo:

- kilómetros por sentido;
- detalle de calles del trazado;
- flota mínima UN11: 27 buses;
- frecuencias en buses/hora por servicio, sentido, hora y tipo de día.

Para el primer escenario se congela una ventana laboral 08:00–08:59:

- C01 ida/regreso: 4 buses/hora -> headway 15 min;
- C02 ida/regreso: 4 buses/hora -> 15 min;
- C03 ida/regreso: 4 buses/hora -> 15 min;
- C03Y ida: 1 bus/hora -> 60 min;
- C03Y regreso: sin expedición durante 08:00–08:59, por lo que se excluye de esta ventana;
- C04 ida/regreso: 2 buses/hora -> 30 min.

## Paradas

Las bases no contienen un listado moderno de paradas. Para habilitar la simulación se usa OpenStreetMap como fuente secundaria, nunca como autoridad de operación:

1. se descargaron 263 nodos `highway=bus_stop` / `public_transport=platform` dentro del bbox de UN11;
2. cada nodo se proyectó contra los shapes oficiales DTPR;
3. se aceptaron nodos a <=120 m del shape;
4. se deduplicaron puntos separados menos de 35 m a lo largo del recorrido.

Resultado: 136 paradas OSM únicas usadas por 9 servicios/sentidos activos en la ventana AM. Los archivos derivados y el catálogo de coordenadas quedan versionados en `data/reference/m7/`.

## Escenario generado

`configs/scenario-villa-alemana-real-am-v1.json`

Versión interna: `villa-alemana-real-network-am-v1`.

Componentes:

- rutas: oficiales DTPR;
- frecuencias: oficiales DTPR Anexo N°3;
- paradas: OSM secundario, map-matched;
- demanda: **sintética y no calibrada**;
- capacidad: **estimada en 35 pasajeros** hasta materializar capacidad de la flota adjudicada;
- tiempo entre paradas: **modelado en 2 min** hasta materializar SUMO/tiempos de viaje.

Por esta razón el nombre `real-network-am` describe la red y oferta, no una calibración completa de operación/demanda.

## Smoke test seed 42

Con la demanda sintética actual, deliberadamente no calibrada:

- baseline: 1.551 pasajeros generados, espera media 26.3921 min, 281 eventos left-behind;
- queue-first: espera media 25.7755 min;
- wait-aware: espera media 25.6547 min;
- connectivity-aware: espera media 26.3899 min.

Estos números **no se interpretan como desempeño real de Villa Alemana**. La demanda sintética satura la red y solo sirve para comprobar que las políticas y el reposicionamiento funcionan sobre la topología M7.

## Próxima calibración prioritaria

1. Procesar EOD SECTRA 2014 para obtener distribución OD/temporal histórica en Villa Alemana/Quilpué.
2. Materializar capacidad/tipología de los 27 buses UN11 adjudicados o una fuente técnica equivalente.
3. Construir red SUMO de los shapes oficiales sobre OSM para sustituir `2 min/parada` por tiempos modelados espacialmente.
4. Ejecutar multi-seed únicamente después de congelar esos tres componentes.

## Regla de interpretación

Hasta completar esos puntos, M7 permite **simular**, desarrollar y verificar políticas, pero no afirmar ahorro porcentual real, capacidad óptima de comodines ni impacto operacional esperado en la ciudad.
