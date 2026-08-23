from __future__ import annotations

import json
import math
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
PERTURBATIONS = {
    "normal": {},
    "C01_half_service": {"C01_I": 2.0, "C01_R": 2.0},
    "C02_half_service": {"C02_I": 2.0, "C02_R": 2.0},
    "C03_half_service": {"C03_I": 2.0, "C03_R": 2.0},
    "C04_half_service": {"C04_I": 2.0, "C04_R": 2.0},
    "C01_C02_half_service": {"C01_I": 2.0, "C01_R": 2.0, "C02_I": 2.0, "C02_R": 2.0},
}


def perturb(scenario, factors):
    lines = tuple(
        replace(line, headway_minutes=max(1, round(line.headway_minutes * factors.get(line.id, 1.0))))
        for line in scenario.lines
    )
    return replace(scenario, lines=lines)


def summarize(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault((row["perturbation"], row["policy"]), []).append(row)
    summary = []
    for (perturbation, policy), subset in sorted(grouped.items()):
        waits = [float(r["mean_wait_minutes"]) for r in subset]
        p95s = [float(r["p95_wait_minutes"]) for r in subset]
        left = [float(r["passengers_left_behind"]) for r in subset]
        boarded = [float(r["boarded_passengers"]) for r in subset]
        mean = statistics.mean(waits)
        sd = statistics.stdev(waits) if len(waits) > 1 else 0.0
        half = 1.96 * sd / math.sqrt(len(waits))
        summary.append({
            "perturbation": perturbation,
            "policy": policy,
            "runs": len(subset),
            "mean_wait_minutes": round(mean, 4),
            "ci95_low": round(mean - half, 4),
            "ci95_high": round(mean + half, 4),
            "mean_p95_wait_minutes": round(statistics.mean(p95s), 4),
            "mean_left_behind": round(statistics.mean(left), 2),
            "mean_boarded_passengers": round(statistics.mean(boarded), 2),
        })
    by_perturbation = {}
    for item in summary:
        by_perturbation.setdefault(item["perturbation"], {})[item["policy"]] = item
    for policies in by_perturbation.values():
        baseline = policies["baseline"]["mean_wait_minutes"]
        for item in policies.values():
            item["wait_improvement_vs_baseline_pct"] = round((baseline - item["mean_wait_minutes"]) / baseline * 100, 2)
    return summary


def main() -> int:
    base = load_scenario("configs/scenario-villa-alemana-real-am-v1.json")
    rows = []
    for perturbation_name, factors in PERTURBATIONS.items():
        scenario = perturb(base, factors)
        for seed in SEEDS:
            for policy_name, runner in POLICIES.items():
                result = runner(scenario, seed).to_dict()
                rows.append({
                    "perturbation": perturbation_name,
                    "seed": seed,
                    "policy": policy_name,
                    **result["metrics"],
                    **result["metadata"],
                })
    summary = summarize(rows)
    output = Path("outputs/m7-resilience")
    output.mkdir(parents=True, exist_ok=True)
    (output / "runs.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
