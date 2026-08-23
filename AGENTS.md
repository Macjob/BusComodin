# AGENTS.md — BusComodin

## Project goal

BusComodin is an experimental, reproducible simulation project for testing whether a small pool of dynamically assigned reinforcement buses can improve public-transport performance while using only predefined services/routes.

The first target is a synthetic scenario. Real-world calibration comes later.

## Core principles

1. **Reproducibility first.** Every experiment must accept a seed and produce deterministic results for the same inputs when technically possible.
2. **Do not tune the benchmark after seeing results.** Scenario definitions, metrics and comparison rules must be versioned.
3. **No LLM in the transport decision loop.** LLMs may help write code/docs/tests, but simulation and dispatch policies must be deterministic and inspectable.
4. **Keep policies comparable.** Baseline and reinforcement strategies must run against the same scenario and demand realization when compared.
5. **Prefer simple models before realistic ones.** Do not import real city data until the synthetic benchmark works end to end.
6. **Do not silently change scope.** Regulatory, tariff, contractual and inter-municipal issues belong in documentation unless explicitly required by the current milestone.
7. **Separate concerns.** Scenario generation, simulation engine, dispatch policy, metrics and experiment orchestration should not be tightly coupled.

## Current milestone: M0

Goal: run a synthetic fixed-network baseline without reinforcement buses.

Expected command shape:

```bash
python -m buscomodin simulate baseline --seed 42
```

Expected outputs:

- machine-readable results (`json` and/or `csv`);
- mean passenger wait time;
- wait-time P95;
- passengers left behind due to capacity;
- occupancy/load metrics;
- observed headways;
- run metadata including seed and scenario version.

## Initial synthetic scenario

Target scale:

- 20–30 stops;
- 3 regular bus lines;
- 2 transfer hubs;
- time-varying synthetic demand during a morning peak;
- finite vehicle capacity;
- fixed schedules/headways;
- no reinforcement buses in M0.

The synthetic network may be simpler than a real road network if that helps validate the experiment pipeline. SUMO integration is preferred, but avoid blocking M0 on unnecessary visual fidelity.

## Planned policies after M0

- `baseline`: fixed network, no reinforcement;
- `dtpm-inspired`: dispatch trigger based on large gaps/crowding thresholds;
- `queue-first`: prioritize largest waiting queue;
- `wait-aware`: prioritize passenger waiting burden;
- `connectivity-aware`: include scarcity of alternatives / network vulnerability.

## Engineering expectations

- Python 3.11+ unless a dependency requires otherwise.
- Prefer small modules with explicit inputs/outputs.
- Type hints for public interfaces.
- Tests for demand generation, metric computation and deterministic seeds.
- Configuration should live in versioned files rather than magic constants spread through code.
- Do not add heavy dependencies without a clear reason.
- Keep generated simulation outputs out of git unless they are small golden/reference fixtures.

## Git workflow

- Work in focused branches.
- Keep commits small and descriptive.
- Link work to the relevant GitHub issue.
- Do not merge experimental policy changes into the baseline implementation without tests.

## Definition of done for M0

M0 is done when a clean checkout can install dependencies, execute the baseline from the CLI, reproduce the same result with the same seed, and run the automated tests successfully.
