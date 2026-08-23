from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import Scenario


DEFAULT_CONNECTIVITY_POLICY_PATH = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "policy-connectivity-aware-v1.json"
)


@dataclass(frozen=True)
class ConnectivityAwareConfig:
    version: str
    wait_burden_weight: float
    capacity_risk_weight: float
    connectivity_vulnerability_weight: float
    minimum_queue: int
    vulnerability_model: str


def load_connectivity_policy(
    path: str | Path | None = None,
) -> ConnectivityAwareConfig:
    config_path = Path(path) if path else DEFAULT_CONNECTIVITY_POLICY_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return ConnectivityAwareConfig(
        version=raw["version"],
        wait_burden_weight=float(raw["weights"]["wait_burden"]),
        capacity_risk_weight=float(raw["weights"]["capacity_risk"]),
        connectivity_vulnerability_weight=float(
            raw["weights"]["connectivity_vulnerability"]
        ),
        minimum_queue=int(raw["minimum_queue"]),
        vulnerability_model=raw["vulnerability_model"],
    )


def regular_line_count_by_stop(scenario: Scenario) -> dict[str, int]:
    counts = {stop: 0 for stop in scenario.stops}
    for line in scenario.lines:
        for stop in line.stops:
            counts[stop] += 1
    return counts


def vulnerability_by_stop(scenario: Scenario) -> dict[str, float]:
    counts = regular_line_count_by_stop(scenario)
    return {stop: 1.0 / count if count > 0 else 1.0 for stop, count in counts.items()}
