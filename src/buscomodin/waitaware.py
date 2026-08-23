from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WAIT_POLICY_PATH = Path(__file__).resolve().parents[2] / "configs" / "policy-wait-aware-v1.json"


@dataclass(frozen=True)
class WaitAwareConfig:
    version: str
    wait_burden_weight: float
    capacity_risk_weight: float
    minimum_queue: int


def load_wait_aware_policy(path: str | Path | None = None) -> WaitAwareConfig:
    config_path = Path(path) if path else DEFAULT_WAIT_POLICY_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return WaitAwareConfig(
        version=raw["version"],
        wait_burden_weight=float(raw["weights"]["wait_burden"]),
        capacity_risk_weight=float(raw["weights"]["capacity_risk"]),
        minimum_queue=int(raw["minimum_queue"]),
    )
