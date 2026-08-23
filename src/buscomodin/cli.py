from __future__ import annotations

import argparse
import json

from .experiments import run_m5, write_m5_results
from .output import write_results
from .scenario import load_scenario
from .simulation import (
    run_baseline,
    run_connectivity_aware,
    run_dtpm_inspired,
    run_queue_first,
    run_wait_aware,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="buscomodin")
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate", help="Run a simulation policy")
    simulate.add_argument(
        "policy",
        choices=["baseline", "queue-first", "dtpm-inspired", "wait-aware", "connectivity-aware"],
    )
    simulate.add_argument("--seed", type=int, default=42)
    simulate.add_argument("--scenario", default=None, help="Path to a versioned scenario JSON")
    simulate.add_argument("--output-dir", default="outputs")
    experiments = subparsers.add_parser("experiments", help="Run versioned experiment suites")
    experiments.add_argument("suite", choices=["m5"])
    experiments.add_argument("--config", default=None)
    experiments.add_argument("--output-dir", default="outputs/m5")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "simulate":
        scenario = load_scenario(args.scenario)
        runners = {
            "baseline": run_baseline,
            "queue-first": run_queue_first,
            "dtpm-inspired": run_dtpm_inspired,
            "wait-aware": run_wait_aware,
            "connectivity-aware": run_connectivity_aware,
        }
        result = runners[args.policy](scenario, args.seed)
        json_path, csv_path = write_results(result, args.output_dir)
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        print(f"JSON: {json_path}")
        print(f"CSV: {csv_path}")
        return 0
    if args.command == "experiments" and args.suite == "m5":
        rows, summary = run_m5(args.config)
        raw_path, summary_path = write_m5_results(args.output_dir, rows, summary)
        print(f"Runs: {len(rows)}")
        print(f"CSV: {raw_path}")
        print(f"Summary: {summary_path}")
        return 0
    return 2
