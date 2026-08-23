# Antecedentes chilenos: Santiago / Red Movilidad

Este documento registra mecanismos operacionales observados en Santiago que pueden servir como precedentes y benchmarks para BusComodin. El objetivo es distinguir claramente entre piezas que ya existen y la hipótesis adicional que queremos evaluar.

## 1. Inyecciones de buses por intervalos y aglomeración

El Manual de Procedimientos del Centro de Monitoreo de Buses (CMB) del DTPM documenta solicitudes de **inyección de buses** ante problemas de regularidad y aglomeraciones.

Entre los gatilladores documentados aparecen intervalos iguales o superiores a 15 minutos por encima del intervalo programado o superiores a dos veces el intervalo programado. También se contempla aglomeración cuando el número estimado de usuarios en una parada supera un umbral asociado a la capacidad del bus tipo.

El manual establece como criterio general una concentración superior a **1,2 veces la capacidad del bus tipo**, aunque la misma tabla operacional contiene valores críticos específicos por tipología de vehículo. Por eso, al implementar un benchmark inspirado en DTPM debemos parametrizar los umbrales y no asumir que una única fórmula representa toda la operación.

Fuente oficial:
- DTPM, Manual de Procedimientos CMB (versión actualizada 01-11-2015): https://www.dtpm.cl/descargas/manuales/PAC%20Version%20Actualizada%2001.11.2015.pdf

### Aplicación a BusComodin

Crear una estrategia `dtpm-inspired` que reaccione a:

- intervalos anormalmente largos;
- acumulación crítica de pasajeros;
- capacidad del vehículo esperado.

Esta estrategia servirá como benchmark realista frente a algoritmos más sofisticados.

## 2. Monitoreo de paradas con cámaras

La memoria DTPM 2014–2017 señala que existían **17 puntos de parada con aglomeración de usuarios** monitoreados mediante cámaras desde el Centro de Monitoreo de Buses. Los monitores podían solicitar inyecciones cuando era necesario.

Fuente oficial:
- DTPM, Memoria 2014–2017: https://www.dtpm.cl/descargas/memoria/Memoria%202014-2017_web2.pdf

### Aplicación a BusComodin

Esto valida conceptualmente la cadena:

`detección de acumulación → evaluación operacional → solicitud de refuerzo`

BusComodin puede simular primero el dato agregado de pasajeros esperando sin comprometerse con una tecnología de detección concreta.

## 3. Escala real de las inyecciones

El Informe de Gestión DTPM reporta que durante 2022 se registraron **14.177 solicitudes de inyecciones de buses** asociadas a amplios intervalos entre buses. El Centro de Monitoreo también gestiona aglomeraciones, congestión, pannes y otros incidentes.

Fuente oficial:
- DTPM, Informe de Gestión 2022: https://www.dtpm.cl/descargas/memoria/InformedeGestion_DTPM_Final%20interactivo.pdf

### Aplicación a BusComodin

Las inyecciones no son solamente una medida excepcional: existe suficiente volumen operacional como para justificar estudiar reglas de asignación y priorización.

## 4. Buses de apoyo y servicios especiales hacia hubs

Durante la paralización ferroviaria de junio de 2024, Red Movilidad dispuso buses de apoyo que conectaban estaciones del servicio Tren Nos con estaciones de Metro. El plan oficial informó **56 buses** realizando servicios especiales ida y vuelta y además el refuerzo de 22 recorridos.

Ejemplos:

- Nos → Metro Hospital El Pino
- 5 Pinos → Metro Hospital El Pino
- San Bernardo → Metro Hospital El Pino
- Lo Espejo → Metro El Parrón
- Lo Valledor → Metro San Alberto Hurtado

Fuentes oficiales:
- Red Movilidad, Plan de Transporte por paro ferroviario de Tren Nos: https://www.red.cl/red-comunica/plan-de-transporte-por-paro-ferroviario-de-tren-nos/
- Red Movilidad / MTT, plan de contingencia: https://www.red.cl/red-comunica/mtt-informa-plan-de-contingencia-por-paro-nacional-de-trabajadores-de-efe/

### Aplicación a BusComodin

Es un precedente directo para nuestro modo **alimentador de conectividad**:

`sector afectado o mal conectado → bus de apoyo → hub con múltiples alternativas`

El proyecto quiere evaluar si esta lógica puede utilizarse de forma más sistemática y preventiva, no solamente durante contingencias mayores.

## 5. Redistribución de buses de apoyo

Durante contingencias de 2019 se utilizaron buses de apoyo a Metro distribuidos entre servicios y extensiones. Por ejemplo, el MTT informó el 6 de diciembre de 2019 que 90 buses de apoyo habían operado ese viernes en estaciones de Metro, distribuidos en 6 servicios y 15 extensiones; para el fin de semana se programaron 27 buses de apoyo en 3 servicios y 10 extensiones.

Fuente oficial:
- MTT, Plan de Transporte 6 diciembre 2019: https://www.mtt.gob.cl/plandetranporte-para-este-fin-de-semana-27-buses-de-apoyo-a-metro-distribuidos-en-3-servicios-y-10-extensiones-de-servicios/

### Aplicación a BusComodin

Demuestra que una flota de apoyo puede distribuirse entre varios servicios según condiciones operacionales. BusComodin quiere formalizar y comparar algoritmos para esa decisión.

## 6. Programación y datos operacionales

El DTPM publica actualmente programas de operación que incluyen, según período y unidad:

- trazados;
- parámetros de operación;
- tablas horarias;
- horarios de pasada por puntos de control;
- registro de paradas.

Fuente oficial:
- DTPM, Programas de Operaciones: https://www.dtpm.cl/index.php/118-programas-de-operaciones

Esto es relevante metodológicamente: muestra qué tipos de datos permiten representar una operación real y orienta qué variables deberíamos buscar más adelante para calibrar un escenario chileno.

## 7. Zonas Pagas como intervención complementaria

DTPM señala que las Zonas Pagas reducen el tiempo de abordaje y que su selección considera demanda de pasajeros, flujo de buses, frecuencia y regularidad.

Fuente oficial:
- DTPM, Zonas Pagas: https://www.dtpm.cl/index.php/infraestructura/zonas-pagas

### Aplicación a BusComodin

Es importante porque una cola grande no implica necesariamente que la única solución sea agregar buses. En experimentos posteriores podemos contrastar **aumento de capacidad** contra **reducción del tiempo de detención/abordaje**.

## Qué ya existe y qué queremos investigar

### Precedentes confirmados

- monitoreo de aglomeraciones;
- control de intervalos y regularidad;
- inyecciones de buses;
- buses de apoyo;
- servicios especiales y refuerzos;
- conexiones temporales hacia hubs multimodales;
- servicios/extensiones predefinidos;
- infraestructura operacional para detectar y responder a incidentes.

### Hipótesis específica de BusComodin

BusComodin no pretende atribuirse la invención de esas piezas. La pregunta experimental es:

> ¿Puede una pequeña flota de refuerzo ser asignada entre servicios predefinidos mediante una política que considere simultáneamente demanda, espera, regularidad y vulnerabilidad de conectividad, obteniendo mejores resultados que reglas reactivas más simples con la misma cantidad de recursos?

## Benchmarks propuestos

1. `baseline` — sin flota comodín.
2. `dtpm-inspired` — reglas de intervalos/agregación inspiradas en procedimientos documentados.
3. `queue-first` — prioriza acumulación.
4. `wait-aware` — incorpora tiempo de espera.
5. `connectivity-aware` — incorpora además escasez de alternativas/conectividad.

Todos deben ejecutarse sobre exactamente las mismas semillas de demanda y tráfico para permitir comparación reproducible.

## Nota metodológica

Los antecedentes de Santiago son **precedentes**, no evidencia de que las mismas reglas sean adecuadas para Villa Alemana ni de que las reglas históricas sigan vigentes sin cambios. Los parámetros históricos se usarán como benchmarks documentados. Para una eventual aplicación real habrá que obtener normativa, operación y datos actuales de la región correspondiente.
