from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from .demand import generate_demand
from .metrics import summarize_metrics
from .models import Passenger, Scenario, Vehicle


@dataclass(frozen=True)
class SimulationResult:
    metadata: dict[str, object]
    metrics: dict[str, float | int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_baseline(scenario: Scenario, seed: int) -> SimulationResult:
    return _run_simulation(scenario, seed, policy="baseline", reinforcement_buses=0)


def run_queue_first(
    scenario: Scenario, seed: int, reinforcement_buses: int = 3
) -> SimulationResult:
    return _run_simulation(
        scenario, seed, policy="queue-first", reinforcement_buses=reinforcement_buses
    )


def _run_simulation(
    scenario: Scenario, seed: int, policy: str, reinforcement_buses: int
) -> SimulationResult:
    passengers = generate_demand(scenario, seed)
    arrivals_by_minute: dict[int, list[Passenger]] = defaultdict(list)
    for passenger in passengers:
        arrivals_by_minute[passenger.arrival_minute].append(passenger)

    queues: dict[str, list[Passenger]] = {stop: [] for stop in scenario.stops}
    events: dict[int, list[tuple[Vehicle, int, bool]]] = defaultdict(list)
    arrivals_history: dict[tuple[str, str], list[int]] = defaultdict(list)
    load_factors: list[float] = []
    wait_times: list[int] = []
    line_by_id = {line.id: line for line in scenario.lines}
    available_reinforcements = reinforcement_buses
    dispatched_reinforcements = 0

    for line in scenario.lines:
        departure = 0
        vehicle_number = 0
        while departure < scenario.duration_minutes:
            vehicle = Vehicle(
                id=f"{line.id}-{vehicle_number}",
                line_id=line.id,
                capacity=scenario.bus_capacity,
            )
            events[departure].append((vehicle, 0, False))
            departure += line.headway_minutes
            vehicle_number += 1

    final_event_minute = (
        scenario.duration_minutes
        + max(len(line.stops) for line in scenario.lines) * scenario.travel_time_minutes
    )
    for minute in range(final_event_minute + 1):
        for passenger in arrivals_by_minute.get(minute, []):
            queues[passenger.origin].append(passenger)

        if policy == "queue-first" and available_reinforcements > 0:
            target = _largest_service_queue(scenario, queues, minute)
            if target is not None and target[0] > 0:
                _, line_id, stop_index = target
                vehicle = Vehicle(
                    id=f"R-{dispatched_reinforcements}",
                    line_id=line_id,
                    capacity=scenario.bus_capacity,
                )
                events[minute].append((vehicle, stop_index, True))
                available_reinforcements -= 1
                dispatched_reinforcements += 1

        for vehicle, stop_index, is_reinforcement in list(events.get(minute, [])):
            line = line_by_id[vehicle.line_id]
            stop = line.stops[stop_index]
            arrivals_history[(line.id, stop)].append(minute)

            remaining_onboard: list[Passenger] = []
            for passenger in vehicle.passengers:
                if passenger.destination == stop:
                    passenger.alighted_minute = minute
                else:
                    remaining_onboard.append(passenger)
            vehicle.passengers = remaining_onboard

            available = vehicle.capacity - len(vehicle.passengers)
            waiting_here = queues[stop]
            eligible = [
                passenger
                for passenger in waiting_here
                if passenger.line_id == line.id and passenger.arrival_minute <= minute
            ]
            to_board = eligible[:available]
            boarded_ids = {passenger.id for passenger in to_board}
            for passenger in to_board:
                passenger.boarded_minute = minute
                wait_times.append(minute - passenger.arrival_minute)
                vehicle.passengers.append(passenger)

            if len(eligible) > available:
                for passenger in eligible[available:]:
                    passenger.left_behind = True

            queues[stop] = [
                passenger for passenger in waiting_here if passenger.id not in boarded_ids
            ]
            load_factors.append(len(vehicle.passengers) / vehicle.capacity)

            if stop_index + 1 < len(line.stops):
                events[minute + scenario.travel_time_minutes].append(
                    (vehicle, stop_index + 1, is_reinforcement)
                )

    headways: list[int] = []
    for arrivals in arrivals_history.values():
        headways.extend(
            second - first for first, second in zip(arrivals, arrivals[1:])
        )

    boarded_count = sum(
        passenger.boarded_minute is not None for passenger in passengers
    )
    metrics = summarize_metrics(
        wait_times=wait_times,
        left_behind_count=sum(passenger.left_behind for passenger in passengers),
        load_factors=load_factors,
        observed_headways=headways,
        generated_passengers=len(passengers),
        boarded_passengers=boarded_count,
    )
    return SimulationResult(
        metadata={
            "policy": policy,
            "seed": seed,
            "scenario_version": scenario.version,
            "duration_minutes": scenario.duration_minutes,
            "bus_capacity": scenario.bus_capacity,
            "regular_lines": len(scenario.lines),
            "reinforcement_buses": reinforcement_buses,
            "reinforcements_dispatched": dispatched_reinforcements,
        },
        metrics=metrics,
    )


def _largest_service_queue(
    scenario: Scenario, queues: dict[str, list[Passenger]], minute: int
) -> tuple[int, str, int] | None:
    candidates: list[tuple[int, str, int]] = []
    for line in scenario.lines:
        for stop_index, stop in enumerate(line.stops[:-1]):
            queue_size = sum(
                passenger.line_id == line.id and passenger.arrival_minute <= minute
                for passenger in queues[stop]
            )
            candidates.append((queue_size, line.id, stop_index))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], item[1], -item[2]))
