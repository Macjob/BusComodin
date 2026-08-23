# ADR 0008 — Primera ingestión de rutas reales/referenciales para M7

## Estado

M7 en progreso. Esta decisión cubre solo la primera ingestión geográfica real.

## Fuente materializada

Se recuperó desde DTPR/MTT el KMZ asociado al proceso ELC0004 (publicado el 07-02-2022), usando la URL directa identificada en el portal oficial:

`https://apps.dtpr.cl/ConsultaLicitaciones/Descargar?documentoId=19145139`

Checksum SHA-256 del KMZ descargado:

`b316bc44e29b0f7c8be4bf8d0d7c91d1cc7dac753481b81c75397af2ba30ff34`

El archivo bruto se mantiene fuera de Git en `data/m7/`. El derivado reproducible se versiona en:

- `data/reference/m7/elc0004-services-120-122-125.geojson`
- `data/reference/m7/elc0004-services-120-122-125.provenance.json`

## Resultado de extracción

El KMZ contiene ida y regreso para los tres servicios priorizados:

- `120_I`
- `120_R`
- `122_I`
- `122_R`
- `125 I`
- `125 R`

Las geometrías se preservan como `LineString` WGS84 lon/lat. No se simplifican ni se map-matchean todavía a SUMO.

## Reproducibilidad

`tools/fetch_m7_sources.py` descarga una fuente declarada en `configs/data-sources-m7-v1.json`, calcula SHA-256 y registra provenance.

`tools/build_m7_reference_routes.py` reconstruye el GeoJSON versionado desde el KMZ descargado.

## GTFS histórico

Se confirmó la URL histórica `valparaiso1feb16.zip` mediante referencias archivísticas, pero el endpoint original de datos.gob.cl actualmente termina en HTTP 404. Por lo tanto, ese feed queda marcado como `historic-2016` y pendiente de recuperación desde archivo/mirror; no se usa como fuente materializada en esta entrega.

## Consecuencia para el modelo

M7 ya dispone de geometrías oficiales/referenciales para reemplazar la forma espacial inventada de LVA1-LVA3. Sin embargo, todavía no se crea `scenario-villa-alemana-real-v1`: faltan paradas reales asociadas a estos trazados y frecuencias/tiempos operacionales suficientemente trazables. Crear ahora un escenario "real" mezclando shapes reales con paraderos sintéticos sería metodológicamente engañoso.

## Próximo paso dentro de M7

1. Extraer de PER0002 2025 condiciones/unidades de servicio y frecuencias relevantes para Villa Alemana.
2. Localizar paradas reales modernas o recuperar/contrastar el GTFS histórico.
3. Map-matchear 120/122/125 sobre la red OSM/SUMO de M6.
4. Solo entonces construir el primer escenario `villa-alemana-real-v1`, inicialmente con demanda aún sintética o EOD histórica claramente separada.
