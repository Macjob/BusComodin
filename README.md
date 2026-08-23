# 🚌 BusComodin

**Simulación abierta de una flota municipal de buses de refuerzo asignados dinámicamente a servicios predefinidos según demanda y vulnerabilidad de conectividad.**

BusComodin explora una pregunta acotada:

> ¿Puede una pequeña flota de buses de refuerzo, reasignada dinámicamente entre recorridos y alimentadores predefinidos, reducir esperas extremas y mejorar la conectividad de sectores con pocas alternativas de transporte?

El proyecto nace pensando en una comuna chilena como caso de estudio, pero la arquitectura y los experimentos deben ser reproducibles en otras ciudades.

## Principio central

BusComodin **no propone rutas libres ni reemplazar la red existente**. Los buses comodín seleccionan entre servicios previamente definidos y complementan la operación normal cuando aparece un problema de demanda o conectividad.

Tres modos iniciales de intervención:

1. **Refuerzo de línea:** agregar capacidad a un recorrido saturado.
2. **Servicio corto:** reforzar únicamente el tramo crítico de un recorrido.
3. **Alimentador:** conectar un sector con pocas alternativas con un nodo de alta conectividad (otras líneas, estación ferroviaria/Metro u otro hub).

## MVP de simulación

Primera etapa deliberadamente sintética:

- 20–30 paraderos.
- 3 recorridos normales.
- 2 nodos de transferencia.
- 3 buses comodín.
- Capacidad limitada por vehículo.
- Demanda variable durante la hora punta.
- Comparación A/B contra la misma red sin buses comodín.

### Estrategias a comparar

- `baseline`: red fija, sin comodines.
- `queue-first`: prioriza la mayor acumulación de pasajeros.
- `wait-aware`: incorpora tiempo de espera.
- `connectivity-aware`: incorpora espera, saturación y escasez de alternativas de transporte.

Una cola pequeña en un sector dependiente de una sola línea puede, por tanto, recibir mayor prioridad que una cola grande en un nodo con muchas alternativas.

## Métricas iniciales

- Tiempo medio de espera.
- P95 de espera.
- Pasajeros que no logran abordar por capacidad.
- Ocupación de vehículos.
- Kilómetros recorridos por buses comodín.
- Kilómetros en vacío.
- Utilización de la flota de refuerzo.
- Accesibilidad/conectividad hacia nodos principales.

## Stack propuesto

- **SUMO** — simulación microscópica de movilidad.
- **Python** — generación de demanda, control, experimentos y análisis.
- **TraCI** — control de SUMO durante la simulación.
- **OpenStreetMap** — red vial para escenarios reales posteriores.
- **OR-Tools** — opcional para etapas posteriores de optimización.

Un LLM **no forma parte del algoritmo de transporte**. Modelos gratuitos/locales pueden ayudar durante el desarrollo, pero las estrategias de despacho deben ser deterministas y reproducibles.

## Alcance

La primera prueba real se mantendrá intencionalmente a escala comunal. Los problemas regulatorios, tarifarios, contractuales y de coordinación intercomunal son importantes, pero se documentarán como restricciones futuras sin bloquear la validación de la hipótesis central.

## Estado

🚧 Etapa inicial: formalización del modelo y construcción del escenario sintético.

## Licencia

MIT (propuesta; agregar archivo LICENSE antes de distribuir código sustantivo).
