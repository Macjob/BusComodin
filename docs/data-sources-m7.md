# Inventario de fuentes para M7 — Gran Valparaíso / Villa Alemana

Fecha de revisión: 2026-08-23.

## Objetivo

Identificar fuentes públicas y preferentemente oficiales que permitan reemplazar gradualmente los supuestos sintéticos de M6 por rutas, paradas, frecuencias, demanda y condiciones operacionales observables. La prioridad es trazabilidad: ningún dato debe presentarse como vigente sin fecha/fuente.

## Prioridad A — DTPR / MTT: licitación Gran Valparaíso 2025

Fuente: https://dtpr.mtt.gob.cl/consultalicitaciones/webpage/Licitaciones.aspx?id=10464

Estado: vigente/relevante para el rediseño regulado del Gran Valparaíso. La licitación PER0002 fue publicada el 01-07-2025 y contiene condiciones de operación, bases, modificaciones, respuestas y antecedentes de adjudicación. Es la fuente prioritaria para extraer el diseño operacional futuro/regulado de la conurbación.

Datos potenciales: unidades de servicio, recorridos, condiciones de operación, frecuencias, flota, terminales, estándares de regularidad y anexos geográficos. Acción M7: descargar e inventariar anexos; extraer tablas y geometrías con versión/fecha.

## Prioridad A — DTPR / MTT: buses eléctricos Quilpué–Villa Alemana

Fuente: https://dtpr.mtt.gob.cl/consultalicitaciones/webpage/ConsultaLicitaciones.aspx?id=3815

Estado: antecedente oficial publicado 07-02-2022. Incluye explícitamente KMZ referenciales. Servicios relevantes: 120 local Villa Alemana, 122 Quilpué–Villa Alemana y 125 Villa Alemana–Quilpué; además 104, 115, 121 y 123.

Datos potenciales: trazados geográficos reales/referenciales y bases técnicas. Acción M7: recuperar el KMZ y convertirlo a GeoJSON; usar 120/122/125 como primer subconjunto real para reemplazar LVA1-LVA3, dejando claro su carácter y fecha.

## Prioridad A — SECTRA: Encuesta Origen Destino Gran Valparaíso 2014

Fuente: https://www.sectra.gob.cl/info-territorial/region-de-valparaiso/

Estado: oficial, histórica pero directamente útil para calibración. SECTRA publica base de datos, zonificación, informe y estudio completo. La ficha reporta 307.203 hogares, población 964.565 y 2.295.100 viajes diarios para la EOD 2014.

Datos potenciales: matrices/patrones origen-destino, propósito, modo, hora y zonificación. Acción M7: descargar base + zonificación y evaluar si Villa Alemana puede aislarse espacialmente. No convertir directamente viajes 2014 en demanda 2026 sin factor/hipótesis explícita.

## Prioridad B — GTFS histórico Gran Valparaíso

Evidencia del dataset: https://datos.gob.cl/km/user/activity/cpacheco

Referencia histórica preservada en Transitland Atlas: el feed aparece asociado a un recurso de datos.gob.cl con un snapshot `valparaiso1feb16.zip` y operadores del Gran Valparaíso.

Estado: histórico (aprox. 2015–2016), no debe tratarse como red vigente. Es valioso para recuperar `stops`, `routes`, `trips`, `stop_times` y `shapes` y contrastarlos con los KMZ/lictación moderna.

Acción M7: intentar recuperar el ZIP histórico o una copia archivada; validar integridad GTFS; filtrar servicios que atraviesen Villa Alemana; comparar geometrías con fuentes DTPR actuales antes de usarlas.

## Prioridad B — DTPR: servicios subsidiados complementarios

Fuente regional: https://dtpr.mtt.gob.cl/ConsultaLicitaciones/WebPage/ConsultasLicitacionesDTPR.aspx?mod=CTR&reg=5

Estado: oficial y actualizado. En la consulta regional aparece, entre otros, CTR0243 Quebrada Escobares–Villa Alemana. Estos servicios pueden representar conectividad periférica que una simulación centrada solo en buses urbanos podría omitir.

Acción M7: inventariar servicios cuyo origen/destino o recorrido toque Villa Alemana y decidir si pertenecen al modelo principal o a una capa de conectividad complementaria.

## Prioridad B — Contenidos esenciales Gran Valparaíso 2024

Fuente: https://dtpr.mtt.gob.cl/consultalicitaciones/webpage/ConsultasContenidos.aspx?id=8345

Estado: oficial. Publica contenido esencial, informe técnico y presentación del nuevo sistema de transporte público mayor del Gran Valparaíso.

Acción M7: usar como contexto y para contrastar supuestos de diseño con las bases 2025; no duplicar datos si existe una versión posterior normativa.

## Prioridad C — Biblioteca Digital MTT / SECTRA

Fuentes:
- https://biblioteca.mtt.gob.cl/
- https://www.sectra.gob.cl/planes_transporte_urbano/valparaiso/documentos_valparaiso.htm

Uso: estudios de transporte, antecedentes de planificación, redes y modelos históricos. Sirven para contexto/calibración secundaria, no necesariamente para representar operación vigente.

## OpenStreetMap / SUMO

OSM sigue siendo la fuente de geometría vial para M6/M7 y SUMO la capa de simulación. OSM no debe utilizarse como autoridad de frecuencias, demanda o vigencia operacional. Las rutas oficiales deben provenir primero de DTPR/MTT/SECTRA y luego map-matchearse sobre OSM.

## Matriz de disponibilidad inicial

| Variable | Mejor fuente identificada | Estado | Uso propuesto M7 |
| --- | --- | --- | --- |
| Calles/geometría vial | OSM | actualizable | red SUMO |
| Rutas Villa Alemana | DTPR KMZ 2022 + licitación 2025 | oficial, distintas fechas | trazados reales/versionados |
| Paradas | GTFS histórico + anexos modernos por localizar | parcial | reconstrucción/contraste |
| Horarios/frecuencias | bases/condiciones DTPR 2025 | por extraer | operación regular |
| Demanda OD | SECTRA EOD 2014 | histórica | calibración con cautela |
| GPS/AVL | estándares/licitación; dataset público aún no localizado | pendiente | no usar hasta localizar fuente |
| GTFS estático vigente | no localizado públicamente en esta revisión | pendiente | buscar/solicitar |
| GTFS-RT vigente | no localizado públicamente en esta revisión | pendiente | buscar/solicitar |
| Servicios periféricos | DTPR CTR región V | oficial | conectividad complementaria |

## Orden de trabajo recomendado para M7

1. Descargar KMZ y bases del proceso 2022; convertir 120/122/125 a GeoJSON.
2. Descargar anexos de PER0002 2025 y localizar recorridos/frecuencias/paradas aplicables a Villa Alemana.
3. Recuperar GTFS histórico y usarlo solo para enriquecer/contrastar IDs, paradas y shapes.
4. Descargar EOD 2014 + zonificación SECTRA y construir un subconjunto Villa Alemana.
5. Map-match de trazados oficiales sobre la red OSM/SUMO de M6.
6. Crear `scenario-villa-alemana-real-v1` con provenance por campo: fuente, fecha, transformación y nivel de confianza.
7. Mantener demanda sintética hasta que la transformación EOD→demanda de simulación esté documentada y validada.

## Regla de provenance

Todo artefacto derivado deberá registrar: URL/fuente, organismo, fecha del documento/dataset, fecha de descarga, licencia si está disponible, transformación aplicada, checksum del archivo original y si el dato representa operación histórica, vigente o propuesta futura.
