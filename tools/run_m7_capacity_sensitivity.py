from __future__ import annotations

import json
import statistics
from dataclasses import replace
from pathlib import Path

from buscomodin.scenario import load_scenario
from buscomodin.simulation import (
    run_baseline,
    run_connectivity_aware,
    run_dtpm_inspired,
    run_queue_first,
    run_wait_aware,
)

POLICIES = {
    "baseline": run_baseline,
    "queue-first": run_queue_first,
    "dtpm-inspired": run_dtpm_inspired,
    "wait-aware": run_wait_aware,
    "connectivity-aware": run_connectivity_aware,
}
SEEDS = [11, 23, 42, 57, 71, 89, 101, 137, 173, 211, 257, 307, 359, 401, 449, 503, 557, 601, 653, 701]
CAPACITIES = [30, 35, 40, 50]


def main() -> int:
    base = load_scenario("configs/scenario-villa-alemana-un11-2025-calibrated-v1.json")
    summary = []
    for capacity in CAPACITIES:
        scenario = replace(base, bus_capacity=capacity)
        results = {name: [] for name in POLICIES}
        for seed in SEEDS:
            for name, runner in POLICIES.items():
                results[name].append(runner(scenario, seed).to_dict())
        baseline_wait = statistics.mean(float(item["metrics"]["mean_wait_minutes"]) for item in results["baseline"])
        for name, items in results.items():
            wait = statistics.mean(float(item["metrics"]["mean_wait_minutes"]) for item in items)
            left = statistics.mean(float(item["metrics"]["passengers_left_behind"]) for item in items)
            max_load = statistics.mean(float(item["metrics"]["max_load_factor"]) for item in items)
            summary.append({
                "capacity": capacity,
                "policy": name,
                "mean_wait_minutes": round(wait, 4),
                "mean_left_behind": round(left, 2),
                "mean_max_load_factor": round(max_load, 4),
                "wait_improvement_vs_baseline_pct": round((baseline_wait - wait) / baseline_wait * 100, 2),
            })
    output = Path("outputs/m7-capacity-sensitivity")
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
