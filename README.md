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

M0–M6 están implementados y M7 mantiene un benchmark histórico/provisional UN11-2025 para Quilpué/Villa Alemana con trazados y frecuencias oficiales, paradas secundarias OSM, calibración histórica provisional y experimentos multi-seed/resiliencia. La operación vigente 2026 debe reconstruirse por separado.

### Revisar resultados M7

Hay dos notebooks complementarios:

- `notebooks/02_m7_review.py`: reproducción compacta de los experimentos.
- `notebooks/03_m7_analysis.py`: dashboard exploratorio con KPIs y gráficos de espera, mejora vs baseline, resiliencia, espera censurada y tasa de servicio.

Ambos usan celdas `# %%`, por lo que pueden abrirse como notebooks interactivos en VS Code/Jupyter. El dashboard vuelve a ejecutar las 20 semillas antes de graficar para evitar resultados desactualizados.

## Ejecutar localmente

Requiere `uv`. El proyecto declara Python 3.11+ y `uv` puede provisionarlo si no está instalado globalmente.

```bash
uv python install 3.11
uv venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m buscomodin simulate baseline --seed 42
```

En Linux/macOS, reemplaza `.venv/Scripts/python.exe` por `.venv/bin/python`.

La CLI escribe resultados machine-readable en `outputs/` (JSON y CSV) y además imprime el resumen por stdout. La misma combinación de escenario versionado y semilla debe producir resultados equivalentes.

El escenario sintético inicial está definido en `configs/scenario-v1.json`. El escenario espacial de referencia de M7 está en `configs/scenario-villa-alemana-un11-2025-spatial-v1.json`.

## Licencia

MIT (propuesta; agregar archivo LICENSE antes de distribuir código sustantivo).
