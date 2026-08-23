# Concepto y límites del experimento

## Hipótesis

Una pequeña flota de buses de reserva, asignable dinámicamente a servicios predefinidos mediante información de demanda, puede reducir episodios de saturación y esperas extremas sin aumentar proporcionalmente la flota permanente.

La hipótesis se amplía con una segunda dimensión: la asignación puede considerar **vulnerabilidad de conectividad**, evitando que sectores dependientes de una única alternativa queden sistemáticamente mal atendidos.

## Qué significa “dinámico”

No significa que cada vehículo invente una ruta. Existe un catálogo autorizado/predefinido de servicios posibles. El controlador decide:

- qué bus de reserva activar;
- qué servicio predefinido ejecutar;
- cuándo despacharlo;
- desde qué punto de espera/base;
- cuándo devolverlo al pool disponible.

Esto convierte el problema principal en uno de **asignación dinámica de capacidad**.

## Tipos de intervención

### 1. Refuerzo de línea
El comodín replica temporalmente un recorrido existente cuando la capacidad regular es insuficiente.

### 2. Servicio corto
El comodín atiende solamente el segmento donde se concentra la demanda y retorna antes de completar un recorrido largo.

### 3. Alimentador de conectividad
El comodín conecta un sector con pocas alternativas con un nodo donde existen múltiples opciones de continuación.

## Vulnerabilidad de conectividad

No toda cola tiene el mismo impacto. Un paradero con 25 pasajeros y una sola alternativa puede representar un problema social mayor que uno con 50 pasajeros servido por varias líneas frecuentes.

Una primera heurística conceptual puede considerar:

`prioridad = f(pasajeros_esperando, tiempo_espera, saturacion, escasez_alternativas, costo_reposicion)`

Los pesos no deben fijarse por intuición: serán parámetros experimentales.

## Incentivos y gobernanza

El sistema real involucra objetivos diferentes:

- pasajeros: tiempo, confiabilidad y accesibilidad;
- operadores: utilización, ingresos y costos;
- municipio/autoridad: cobertura, equidad territorial y continuidad;
- red regional: coordinación y regulación.

El MVP **no intenta resolver este mecanismo institucional**. Primero se probará si existe un beneficio operacional medible. Incentivos, regulación, tarifas y contratos se mantendrán documentados como una capa posterior.

## Regla de alcance

Si una cuestión política, tarifaria, legal o intercomunal no es necesaria para probar la hipótesis operacional, se registra como restricción futura en vez de incorporarla al MVP.
