from __future__ import annotations

import csv
import json
import math
import statistics
from dataclasses import replace
from pathlib import Path

from .models import DemandConfig, Line, Scenario
from .scenario import load_scenario
from .simulation import (
    run_baseline,
    run_connectivity_aware,
    run_dtpm_inspired,
    run_queue_first,
    run_wait_aware,
)

DEFAULT_EXPERIMENT_PATH = Path(__file__).resolve().parents[2] / "configs" / "experiments-m5-v1.json"
RUNNERS = {
    "baseline": run_baseline,
    "queue-first": run_queue_first,
    "dtpm-inspired": run_dtpm_inspired,
    "wait-aware": run_wait_aware,
    "connectivity-aware": run_connectivity_aware,
}


def load_experiment_config(path: str | Path | None = None) -> dict[str, object]:
    return json.loads((Path(path) if path else DEFAULT_EXPERIMENT_PATH).read_text(encoding="utf-8"))


def vary_scenario(scenario: Scenario, dimension: str, value: object) -> Scenario:
    if dimension == "demand_multiplier":
        demand = replace(scenario.demand, base_rate_per_stop_minute=scenario.demand.base_rate_per_stop_minute * float(value))
        return replace(scenario, demand=demand)
    if dimension == "capacity_multiplier":
        return replace(scenario, bus_capacity=max(1, round(scenario.bus_capacity * float(value))))
    if dimension == "headway_multiplier":
        lines = tuple(replace(line, headway_minutes=max(1, round(line.headway_minutes * float(value)))) for line in scenario.lines)
        return replace(scenario, lines=lines)
    if dimension == "congestion_multiplier":
        return replace(scenario, travel_time_minutes=max(1, round(scenario.travel_time_minutes * float(value))))
    if dimension == "partial_line_failure":
        if value == "none":
            return scenario
        lines = tuple(replace(line, headway_minutes=line.headway_minutes * 2) if line.id == value else line for line in scenario.lines)
        return replace(scenario, lines=lines)
    raise ValueError(f"Unknown sensitivity dimension: {dimension}")


def _run(policy: str, scenario: Scenario, seed: int, buses: int) -> dict[str, object]:
    if policy == "baseline":
        result = RUNNERS[policy](scenario, seed)
    else:
        result = RUNNERS[policy](scenario, seed, reinforcement_buses=buses)
    return result.to_dict()


def run_m5(config_path: str | Path | None = None) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    config = load_experiment_config(config_path)
    base = load_scenario()
    seeds = config["seeds"]
    policies = config["policies"]
    rows: list[dict[str, object]] = []

    cases = [("base", 1.0)]
    for dimension, values in config["sensitivity"].items():
        cases.extend((dimension, value) for value in values if not (dimension != "partial_line_failure" and float(value) == 1.0) and not (dimension == "partial_line_failure" and value == "none"))

    for dimension, value in cases:
        scenario = base if dimension == "base" else vary_scenario(base, dimension, value)
        for seed in seeds:
            for policy in policies:
                result = _run(policy, scenario, int(seed), 3)
                rows.append({"dimension": dimension, "value": value, "seed": seed, "policy": policy, **result["metrics"]})

    # Marginal bus experiment on the unmodified scenario for reinforcement policies.
    for buses in config["reinforcement_buses"]:
        for seed in seeds:
            for policy in policies:
                if policy == "baseline":
                    continue
                result = _run(policy, base, int(seed), int(buses))
                rows.append({"dimension": "reinforcement_buses", "value": buses, "seed": seed, "policy": policy, **result["metrics"]})

    grouped: dict[tuple[str, str, str], list[float]] = {}
    for row in rows:
        key = (str(row["dimension"]), str(row["value"]), str(row["policy"]))
        grouped.setdefault(key, []).append(float(row["mean_wait_minutes"]))
    summary = []
    for (dimension, value, policy), waits in sorted(grouped.items()):
        mean = statistics.mean(waits)
        sd = statistics.stdev(waits) if len(waits) > 1 else 0.0
        half = 1.96 * sd / math.sqrt(len(waits)) if waits else 0.0
        summary.append({"dimension": dimension, "value": value, "policy": policy, "runs": len(waits), "mean_wait_minutes": round(mean, 4), "ci95_low": round(mean - half, 4), "ci95_high": round(mean + half, 4)})
    return rows, summary


def write_m5_results(output_dir: str | Path, rows: list[dict[str, object]], summary: list[dict[str, object]]) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / "m5-runs.csv"
    summary_path = output / "m5-summary.json"
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return raw_path, summary_path
