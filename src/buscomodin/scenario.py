from __future__ import annotations

import json
from pathlib import Path

from .models import DemandConfig, Line, Scenario


DEFAULT_SCENARIO_PATH = Path(__file__).resolve().parents[2] / "configs" / "scenario-v1.json"


def load_scenario(path: str | Path | None = None) -> Scenario:
    config_path = Path(path) if path else DEFAULT_SCENARIO_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return Scenario(
        version=raw["version"],
        duration_minutes=int(raw["duration_minutes"]),
        travel_time_minutes=int(raw["travel_time_minutes"]),
        bus_capacity=int(raw["bus_capacity"]),
        stops=tuple(raw["stops"]),
        hubs=tuple(raw["hubs"]),
        lines=tuple(
            Line(
                id=line["id"],
                headway_minutes=int(line["headway_minutes"]),
                stops=tuple(line["stops"]),
                segment_travel_minutes=(
                    tuple(int(value) for value in line["segment_travel_minutes"])
                    if "segment_travel_minutes" in line
                    else None
                ),
            )
            for line in raw["lines"]
        ),
        demand=DemandConfig(**raw["demand"]),
    )
