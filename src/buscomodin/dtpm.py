from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import Scenario


DEFAULT_DTPM_POLICY_PATH = Path(__file__).resolve().parents[2] / "configs" / "policy-dtpm-inspired-v1.json"


@dataclass(frozen=True)
class ShortService:
    id: str
    line_id: str
    start_stop: str
    end_stop: str


@dataclass(frozen=True)
class DtpmPolicyConfig:
    version: str
    absolute_extra_minutes: int
    multiple_of_scheduled: float
    capacity_multiplier: float
    short_services: tuple[ShortService, ...]


def load_dtpm_policy(path: str | Path | None = None) -> DtpmPolicyConfig:
    config_path = Path(path) if path else DEFAULT_DTPM_POLICY_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return DtpmPolicyConfig(
        version=raw["version"],
        absolute_extra_minutes=int(raw["headway"]["absolute_extra_minutes"]),
        multiple_of_scheduled=float(raw["headway"]["multiple_of_scheduled"]),
        capacity_multiplier=float(raw["crowding"]["capacity_multiplier"]),
        short_services=tuple(ShortService(**item) for item in raw["short_services"]),
    )


def choose_short_service_end(
    scenario: Scenario,
    config: DtpmPolicyConfig,
    line_id: str,
    start_index: int,
) -> int | None:
    line = next(line for line in scenario.lines if line.id == line_id)
    for service in config.short_services:
        if service.line_id != line_id:
            continue
        service_start = line.stops.index(service.start_stop)
        service_end = line.stops.index(service.end_stop)
        if service_start <= start_index < service_end:
            return service_end
    return None
