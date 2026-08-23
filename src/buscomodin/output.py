from __future__ import annotations

import csv
import json
from pathlib import Path

from .simulation import SimulationResult


def write_results(result: SimulationResult, output_dir: str | Path) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    seed = result.metadata["seed"]
    policy = result.metadata["policy"]
    json_path = directory / f"{policy}-seed-{seed}.json"
    csv_path = directory / f"{policy}-seed-{seed}.csv"

    json_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    row = {**result.metadata, **result.metrics}
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    return json_path, csv_path
