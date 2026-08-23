from __future__ import annotations

import argparse
import json

from .output import write_results
from .scenario import load_scenario
from .simulation import run_baseline, run_dtpm_inspired, run_queue_first


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="buscomodin")
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate", help="Run a simulation policy")
    simulate.add_argument("policy", choices=["baseline", "queue-first", "dtpm-inspired"])
    simulate.add_argument("--seed", type=int, default=42)
    simulate.add_argument("--scenario", default=None, help="Path to a versioned scenario JSON")
    simulate.add_argument("--output-dir", default="outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "simulate":
        scenario = load_scenario(args.scenario)
        runners = {
            "baseline": run_baseline,
            "queue-first": run_queue_first,
            "dtpm-inspired": run_dtpm_inspired,
        }
        result = runners[args.policy](scenario, args.seed)
        json_path, csv_path = write_results(result, args.output_dir)
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        print(f"JSON: {json_path}")
        print(f"CSV: {csv_path}")
        return 0
    return 2
