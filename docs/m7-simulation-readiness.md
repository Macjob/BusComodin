# M7 — Checklist de datos para iniciar simulación realista

## Objetivo

Construir `scenario-villa-alemana-real-v1` sin presentar como reales parámetros que aún sean estimados. El escenario inicial puede combinar red/oferta real con demanda histórica calibrada, siempre que cada capa quede etiquetada.

## Fuentes confirmadas

### 1. Red vigente UN11 — prioridad máxima

Fuente oficial DTPR: concurso `DSL4654 - UN11`, publicado 22-10-2024.

Servicios vigentes/relevantes identificados: `C01`, `C02`, `C03`, `C03Y`, `C04` para Quilpué/Villa Alemana.

Artefactos a materializar:
- KMZ Servicios UN11.
- Bases de Licitación / Decreto Exento N°4515/2024.
- Programa de Operación, Anexo N°3.
- Contrato UN11 aprobado por Decreto Exento N°792/2025 como control de vigencia.

Uso esperado:
- shapes/trazados;
- frecuencias por periodo y tipo de día;
- horarios/expediciones si están disponibles;
- terminales y condiciones de operación;
- flota/capacidad cuando el documento lo permita.

### 2. Paradas

Prioridad:
1. Anexos/programa operacional UN11 si contienen paradas o puntos de control.
2. Dataset/GTFS oficial moderno de Gran Valparaíso si se localiza.
3. OpenStreetMap como fuente secundaria para ubicación/contraste, etiquetada como tal.

Regla: no convertir vértices del shape en paradas inventadas.

### 3. Red vial y tiempos

OSM + SUMO, pipeline ya definido en M6.

Uso:
- map matching de shapes oficiales;
- distancias de servicio;
- reposicionamiento de buses comodín;
- tiempos base de circulación cuando no exista tiempo programado más autoritativo.

Los tiempos SUMO serán `modelados`, no `observados`.

### 4. Demanda

Fuente confirmada: EOD Gran Valparaíso 2014 de SECTRA, con base y zonificación.

Uso inicial:
- distribución espacial y temporal OD histórica;
- calibración relativa de demanda por zona/franja;
- no representar como volumen 2026 sin factor de actualización respaldado.

Si no existe matriz actual pública, `real-v1` deberá declarar `demand_status = historical-calibrated`.

### 5. Irregularidad operacional

Fuente: Informe Técnico DTPR Gran Valparaíso asociado a PER0002, con antecedentes de expediciones exigidas/observadas y cumplimiento durante agosto 2022–julio 2023.

Uso:
- construir escenarios de perturbación/calidad operacional;
- calibrar dispersión/fallos parciales de forma separada de la frecuencia nominal.

No usar agregados del sistema como si fueran métricas específicas de UN11 sin desagregación comprobada.

### 6. Capacidad/flota

Buscar en bases/contrato UN11:
- número de buses;
- tipología/longitud;
- capacidad nominal;
- reserva operacional si está definida.

Si solo hay tipología, la capacidad puede provenir de ficha técnica homologada, registrando fuente separada.

### 7. Buses comodín

Siguen siendo dimensión experimental, no dato observado.

Parámetros a definir sobre la red real:
- cantidad: sensibilidad 1–5, no fijar 3 como óptimo;
- bases/hubs: terminales/puntos reales cuando estén identificados;
- reposicionamiento: red vial SUMO;
- política: mismas políticas M1–M4, sin recalibrarlas mirando M7.

## Dataset histórico conservado

ELC0004 2022: servicios 120/122/125, seis geometrías ida/vuelta ya materializadas con checksum. Se conserva como antecedente histórico y posible escenario comparativo; no es la base operacional vigente de `real-v1`.

## Gate mínimo para ejecutar `real-v1`

Obligatorio antes de etiquetar el escenario como realista:
- [ ] shapes C01/C02/C03/C03Y/C04 materializados con provenance;
- [ ] frecuencia/oferta UN11 materializada por tipo de día/franja;
- [ ] paradas o puntos operacionales con fuente trazable;
- [ ] shapes map-matcheados a OSM/SUMO o distancia/tiempo equivalente trazable;
- [ ] capacidad de bus documentada o marcada explícitamente como estimada;
- [ ] demanda EOD procesada para las zonas relevantes y marcada histórica;
- [ ] hubs iniciales de comodines definidos sin teletransporte;
- [ ] configuración completa versionada y checksums de fuentes.

## Gate deseable, no bloqueante

- AVL/GPS observado moderno;
- validaciones/recaudación electrónica;
- velocidades observadas por tramo;
- demanda 2025/2026;
- ocupación observada por servicio.

La ausencia de estos datos no impide una primera simulación realista, pero limita las conclusiones operacionales.

## Primer experimento una vez abierto el gate

1. Día laboral, punta AM.
2. Baseline UN11 sin comodines.
3. Mismas semillas de demanda calibrada para todas las políticas.
4. 1–5 comodines.
5. Operación normal y perturbaciones separadas.
6. Métricas M0–M5 + km/minutos de reposicionamiento y utilización de comodines.
7. No optimizar pesos/políticas en el mismo conjunto usado para evaluar.
