from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from buscomodin.geography import load_villa_alemana_geo, sumo_import_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import Villa Alemana from OSM and build a SUMO network")
    parser.add_argument("--sumo-home", default=os.environ.get("SUMO_HOME"))
    parser.add_argument("--output-dir", default="data/villa-alemana-sumo")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.sumo_home:
        raise SystemExit("SUMO_HOME is required (or pass --sumo-home)")
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    config = load_villa_alemana_geo()
    commands = sumo_import_commands(config, args.sumo_home, output)
    for command in commands:
        print(" ".join(str(part) for part in command))
        if not args.dry_run:
            subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
