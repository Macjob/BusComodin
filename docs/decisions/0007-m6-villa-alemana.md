# ADR 0007 — Escenario Villa Alemana simplificado (M6)

## Estado

Aceptado para M6.

## Objetivo

M6 introduce geografía real sin adelantar la calibración de M7. La red se ancla en cinco estaciones reales del Tren Limache–Puerto dentro de Villa Alemana: Las Américas, La Concepción, Villa Alemana, Sargento Aldea y Peñablanca.

La capa geográfica queda versionada en `configs/villa-alemana-geo-v1.json`, con un bounding box acotado y coordenadas de las cinco estaciones. La descarga y conversión OSM→SUMO se automatiza en `tools/build_villa_alemana_sumo.py` mediante `osmGet.py` y `osmBuild.py`.

## Separación de capas

M6 mantiene dos artefactos distintos:

1. `villa-alemana-geo-v1.json`: geografía, bbox, anclas y parámetros de importación SUMO.
2. `scenario-villa-alemana-v1.json`: escenario simplificado compatible con el core actual, con 20 paraderos, 3 líneas y demanda sintética.

Los paraderos `M_*` corresponden a las cinco anclas reales; los nodos `VAxx` son macro-nodos sintéticos de corredor y no deben interpretarse como paraderos reales. Las líneas `LVA1-LVA3` son rutas experimentales simplificadas, no servicios reales de Red Valparaíso de Movilidad.

## Pipeline SUMO

Con SUMO instalado y `SUMO_HOME` configurado:

```bash
python tools/build_villa_alemana_sumo.py --output-dir data/villa-alemana-sumo
```

Para inspeccionar los comandos sin descargar ni construir:

```bash
python tools/build_villa_alemana_sumo.py --sumo-home C:/SUMO --dry-run
```

Los archivos generados bajo `data/villa-alemana-sumo/` no se versionan. El config y el script sí se versionan para poder reconstruirlos.

## Decisión metodológica

No se usa todavía demanda real, frecuencias observadas de buses, tiempos de viaje calibrados, trazados reales de líneas de superficie ni aforos. Las políticas M0–M4 se reutilizan sin modificación. Esto permite probar que el motor funciona sobre una topología inspirada en Villa Alemana sin confundir geografía con calibración operacional.

## Validación del core

Con seed 42 sobre `villa-alemana-simplified-v1`, el baseline genera 681 pasajeros y registra 5.5755 minutos de espera media. La política connectivity-aware, sin ningún cambio de implementación, registra 5.0211 minutos con los mismos 681 pasajeros. Esta comparación solo demuestra compatibilidad del escenario con el motor; no se interpreta como evidencia operacional sobre Villa Alemana porque la demanda y las rutas siguen siendo sintéticas.

## Limitación de entorno

El host actual de CodexPro no tiene SUMO instalado, por lo que M6 valida el generador de comandos con tests y `--dry-run`, pero no afirma haber construido localmente el archivo `.net.xml`. La materialización de la red SUMO queda preparada y reproducible para un host con SUMO.

## Fuera de alcance

Demanda real, líneas reales de buses, frecuencias observadas, GTFS/AVL, calibración de capacidad, tiempos de caminata y conexiones multimodales detalladas corresponden a M7.
