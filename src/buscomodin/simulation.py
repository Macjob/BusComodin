from __future__ import annotations

from collections import defaultdict, deque
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


@dataclass
class ReinforcementState:
    id: str
    location: str
    available: bool = True
    assignments: int = 0
    reposition_minutes: int = 0


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
    events: dict[int, list[tuple[Vehicle, int, str | None]]] = defaultdict(list)
    arrivals_history: dict[tuple[str, str], list[int]] = defaultdict(list)
    load_factors: list[float] = []
    wait_times: list[int] = []
    line_by_id = {line.id: line for line in scenario.lines}
    stop_graph = _build_stop_graph(scenario)
    reinforcements = _build_reinforcement_pool(scenario, reinforcement_buses)

    for line in scenario.lines:
        departure = 0
        vehicle_number = 0
        while departure < scenario.duration_minutes:
            vehicle = Vehicle(
                id=f"{line.id}-{vehicle_number}",
                line_id=line.id,
                capacity=scenario.bus_capacity,
            )
            events[departure].append((vehicle, 0, None))
            departure += line.headway_minutes
            vehicle_number += 1

    final_event_minute = (
        scenario.duration_minutes
        + 2 * len(scenario.stops) * scenario.travel_time_minutes
    )
    for minute in range(final_event_minute + 1):
        for passenger in arrivals_by_minute.get(minute, []):
            queues[passenger.origin].append(passenger)

        if policy == "queue-first" and minute < scenario.duration_minutes:
            for reinforcement in reinforcements:
                if not reinforcement.available:
                    continue
                target = _largest_service_queue(scenario, queues, minute)
                if target is None or target[0] <= 0:
                    break
                _, line_id, stop_index = target
                target_stop = line_by_id[line_id].stops[stop_index]
                reposition = _reposition_minutes(
                    stop_graph,
                    reinforcement.location,
                    target_stop,
                    scenario.travel_time_minutes,
                )
                vehicle = Vehicle(
                    id=reinforcement.id,
                    line_id=line_id,
                    capacity=scenario.bus_capacity,
                )
                events[minute + reposition].append(
                    (vehicle, stop_index, reinforcement.id)
                )
                reinforcement.available = False
                reinforcement.assignments += 1
                reinforcement.reposition_minutes += reposition

        for vehicle, stop_index, reinforcement_id in list(events.get(minute, [])):
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
                    (vehicle, stop_index + 1, reinforcement_id)
                )
            elif reinforcement_id is not None:
                reinforcement = next(
                    item for item in reinforcements if item.id == reinforcement_id
                )
                reinforcement.location = stop
                reinforcement.available = True

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
    total_assignments = sum(item.assignments for item in reinforcements)
    total_reposition_minutes = sum(item.reposition_minutes for item in reinforcements)
    return SimulationResult(
        metadata={
            "policy": policy,
            "seed": seed,
            "scenario_version": scenario.version,
            "duration_minutes": scenario.duration_minutes,
            "bus_capacity": scenario.bus_capacity,
            "regular_lines": len(scenario.lines),
            "reinforcement_buses": reinforcement_buses,
            "reinforcement_assignments": total_assignments,
            "reinforcement_reposition_minutes": total_reposition_minutes,
        },
        metrics=metrics,
    )


def _build_reinforcement_pool(
    scenario: Scenario, reinforcement_buses: int
) -> list[ReinforcementState]:
    if reinforcement_buses <= 0:
        return []
    bases = scenario.hubs or scenario.stops[:1]
    return [
        ReinforcementState(id=f"R-{index}", location=bases[index % len(bases)])
        for index in range(reinforcement_buses)
    ]


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


def _build_stop_graph(scenario: Scenario) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {stop: set() for stop in scenario.stops}
    for line in scenario.lines:
        for first, second in zip(line.stops, line.stops[1:]):
            graph[first].add(second)
            graph[second].add(first)
    return graph


def _reposition_minutes(
    graph: dict[str, set[str]], origin: str, destination: str, travel_time_minutes: int
) -> int:
    if origin == destination:
        return 0
    queue: deque[tuple[str, int]] = deque([(origin, 0)])
    visited = {origin}
    while queue:
        stop, hops = queue.popleft()
        for neighbour in sorted(graph[stop]):
            if neighbour in visited:
                continue
            if neighbour == destination:
                return (hops + 1) * travel_time_minutes
            visited.add(neighbour)
            queue.append((neighbour, hops + 1))
    raise ValueError(f"No reposition path from {origin} to {destination}")
