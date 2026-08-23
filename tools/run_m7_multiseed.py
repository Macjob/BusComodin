from __future__ import annotations

import argparse
import json
import math
import statistics
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run M7 multi-seed comparison")
    parser.add_argument("--scenario", default="configs/scenario-villa-alemana-real-am-v1.json")
    parser.add_argument("--output-dir", default="outputs/m7-multiseed")
    args = parser.parse_args()
    scenario = load_scenario(args.scenario)
    rows = []
    for seed in SEEDS:
        for name, runner in POLICIES.items():
            result = runner(scenario, seed).to_dict()
            rows.append({"seed": seed, "policy": name, **result["metrics"], **result["metadata"]})

    summary = []
    for name in POLICIES:
        subset = [row for row in rows if row["policy"] == name]
        waits = [float(row["mean_wait_minutes"]) for row in subset]
        p95s = [float(row["p95_wait_minutes"]) for row in subset]
        left = [float(row["passengers_left_behind"]) for row in subset]
        boarded = [float(row["boarded_passengers"]) for row in subset]
        mean = statistics.mean(waits)
        sd = statistics.stdev(waits) if len(waits) > 1 else 0.0
        half = 1.96 * sd / math.sqrt(len(waits))
        summary.append(
            {
                "policy": name,
                "runs": len(subset),
                "mean_wait_minutes": round(mean, 4),
                "ci95_low": round(mean - half, 4),
                "ci95_high": round(mean + half, 4),
                "mean_p95_wait_minutes": round(statistics.mean(p95s), 4),
                "mean_left_behind": round(statistics.mean(left), 2),
                "mean_boarded_passengers": round(statistics.mean(boarded), 2),
            }
        )

    baseline = next(item for item in summary if item["policy"] == "baseline")["mean_wait_minutes"]
    for item in summary:
        item["wait_improvement_vs_baseline_pct"] = round((baseline - item["mean_wait_minutes"]) / baseline * 100, 2)

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "runs.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
