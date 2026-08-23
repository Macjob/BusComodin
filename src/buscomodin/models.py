from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Line:
    id: str
    headway_minutes: int
    stops: tuple[str, ...]


@dataclass(frozen=True)
class DemandConfig:
    base_rate_per_stop_minute: float
    peak_start_minute: int
    peak_end_minute: int
    peak_multiplier: float
    hub_origin_multiplier: float


@dataclass(frozen=True)
class Scenario:
    version: str
    duration_minutes: int
    travel_time_minutes: int
    bus_capacity: int
    stops: tuple[str, ...]
    hubs: tuple[str, ...]
    lines: tuple[Line, ...]
    demand: DemandConfig


@dataclass
class Passenger:
    id: int
    arrival_minute: int
    origin: str
    destination: str
    line_id: str
    boarded_minute: int | None = None
    alighted_minute: int | None = None
    left_behind: bool = False


@dataclass
class Vehicle:
    id: str
    line_id: str
    capacity: int
    passengers: list[Passenger] = field(default_factory=list)
