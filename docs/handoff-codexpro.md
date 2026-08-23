# Handoff para CodexPro

Este archivo permite retomar BusComodin desde una sesión nueva sin depender del historial de ChatGPT.

## Contexto mínimo

BusComodin es un experimento abierto de simulación de transporte público. La hipótesis es que una pequeña flota de buses de refuerzo, asignada dinámicamente entre servicios predefinidos, puede reducir saturación, esperas extremas y vulnerabilidad de sectores con pocas alternativas de transporte.

No se proponen rutas libres. Los comodines seleccionan entre recorridos, servicios cortos y alimentadores predefinidos.

## Antes de modificar código

Lee, en este orden:

1. `README.md`
2. `AGENTS.md`
3. `docs/concept.md`
4. `docs/precedents/chile-santiago.md`
5. `docs/roadmap.md`
6. Issues abiertos de GitHub, empezando por el milestone más bajo aún no completado.

Luego inspecciona el estado actual del repositorio y ejecuta los tests existentes antes de hacer cambios.

## Objetivo de la siguiente sesión

Si M0 sigue abierto, implementar **M0 — Baseline sintético reproducible** del issue #1.

Criterio principal de aceptación:

```bash
pytest
python -m buscomodin simulate baseline --seed 42
```

La misma semilla debe producir resultados equivalentes/deterministas.

## Alcance M0

- paquete Python estructurado;
- escenario sintético con 20–30 paraderos;
- 3 líneas regulares;
- 2 nodos de transferencia;
- demanda sintética variable en hora punta;
- capacidad limitada por vehículo;
- sin buses comodín todavía;
- métricas: espera media, P95, pasajeros dejados atrás, ocupación y headways;
- resultados JSON/CSV;
- tests con pytest;
- notebook `notebooks/01_baseline.ipynb` que consuma el mismo core;
- preparación limpia para integración posterior con SUMO/TraCI.

Si SUMO bloquea el entorno, implementar primero un motor sintético desacoplado en Python y mantener una interfaz clara para un backend SUMO posterior. No duplicar lógica en notebooks.

## Restricciones metodológicas

- No introducir un LLM dentro del algoritmo de transporte.
- No implementar todavía `queue-first`, `DTPM-inspired`, `wait-aware` ni `connectivity-aware` durante M0.
- No usar datos reales todavía.
- No modificar métricas, escenarios o seeds para favorecer resultados.
- Mantener separadas generación de demanda, simulación, políticas y métricas.
- Todo parámetro del experimento debe quedar explícito y versionado.

## Forma de trabajo

1. Crear una rama para el milestone.
2. Implementar el alcance mínimo completo.
3. Ejecutar tests y CLI de aceptación.
4. Documentar decisiones relevantes.
5. Abrir un PR pequeño y revisable enlazando el issue correspondiente.
6. No empezar el siguiente milestone antes de cerrar/revisar el actual.

## Después de M0

Seguir `docs/roadmap.md`:

- M1: Queue-first.
- M2: DTPM-inspired.
- M3: Wait-aware.
- M4: Connectivity-aware.
- M5: experimentos multi-seed.
- M6: Villa Alemana simplificada.
- M7: calibración con datos reales.

## Prompt corto reusable

> Retoma el repositorio `Macjob/BusComodin`. Lee `README.md`, `AGENTS.md`, `docs/concept.md`, `docs/precedents/chile-santiago.md`, `docs/roadmap.md` y `docs/handoff-codexpro.md`, además de los issues abiertos. Identifica el milestone más bajo no completado y ejecútalo respetando su alcance y criterios de aceptación. Trabaja en una rama separada, ejecuta tests, documenta decisiones y abre un PR. No avances al milestone siguiente en la misma sesión salvo que el actual quede completamente cerrado y revisado.
