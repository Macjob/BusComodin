from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import heapq

from .connectivity import load_connectivity_policy, vulnerability_by_stop
from .demand import generate_demand
from .dtpm import choose_short_service_end, load_dtpm_policy
from .metrics import summarize_metrics
from .models import Passenger, Scenario, Vehicle
from .waitaware import load_wait_aware_policy


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


def run_dtpm_inspired(
    scenario: Scenario, seed: int, reinforcement_buses: int = 3
) -> SimulationResult:
    return _run_simulation(
        scenario, seed, policy="dtpm-inspired", reinforcement_buses=reinforcement_buses
    )


def run_wait_aware(
    scenario: Scenario, seed: int, reinforcement_buses: int = 3
) -> SimulationResult:
    return _run_simulation(
        scenario, seed, policy="wait-aware", reinforcement_buses=reinforcement_buses
    )


def run_connectivity_aware(
    scenario: Scenario, seed: int, reinforcement_buses: int = 3
) -> SimulationResult:
    return _run_simulation(
        scenario,
        seed,
        policy="connectivity-aware",
        reinforcement_buses=reinforcement_buses,
    )


def _run_simulation(
    scenario: Scenario, seed: int, policy: str, reinforcement_buses: int
) -> SimulationResult:
    passengers = generate_demand(scenario, seed)
    arrivals_by_minute: dict[int, list[Passenger]] = defaultdict(list)
    for passenger in passengers:
        arrivals_by_minute[passenger.arrival_minute].append(passenger)

    queues: dict[str, list[Passenger]] = {stop: [] for stop in scenario.stops}
    events: dict[int, list[tuple[Vehicle, int, str | None, int]]] = defaultdict(list)
    arrivals_history: dict[tuple[str, str], list[int]] = defaultdict(list)
    regular_last_arrival: dict[tuple[str, str], int] = {}
    load_factors: list[float] = []
    wait_times: list[int] = []
    line_by_id = {line.id: line for line in scenario.lines}
    stop_graph = _build_stop_graph(scenario)
    reinforcements = _build_reinforcement_pool(scenario, reinforcement_buses)
    dtpm_config = load_dtpm_policy() if policy == "dtpm-inspired" else None
    wait_config = load_wait_aware_policy() if policy == "wait-aware" else None
    connectivity_config = (
        load_connectivity_policy() if policy == "connectivity-aware" else None
    )
    connectivity_vulnerability = (
        vulnerability_by_stop(scenario) if connectivity_config is not None else None
    )
    short_service_assignments = 0

    for line in scenario.lines:
        departure = 0
        vehicle_number = 0
        while departure <= scenario.duration_minutes:
            vehicle = Vehicle(
                id=f"{line.id}-{vehicle_number}",
                line_id=line.id,
                capacity=scenario.bus_capacity,
            )
            events[departure].append((vehicle, 0, None, len(line.stops) - 1))
            departure += line.headway_minutes
            vehicle_number += 1

    final_event_minute = scenario.duration_minutes + 2 * len(scenario.stops) * scenario.travel_time_minutes
    for minute in range(final_event_minute + 1):
        for passenger in arrivals_by_minute.get(minute, []):
            queues[passenger.origin].append(passenger)

        if minute < scenario.duration_minutes and policy in {"queue-first", "dtpm-inspired", "wait-aware", "connectivity-aware"}:
            for reinforcement in reinforcements:
                if not reinforcement.available:
                    continue
                if policy == "queue-first":
                    target = _largest_service_queue(scenario, queues, minute)
                elif policy == "dtpm-inspired":
                    assert dtpm_config is not None
                    target = _dtpm_target(
                        scenario, queues, minute, regular_last_arrival, dtpm_config
                    )
                elif policy == "wait-aware":
                    assert wait_config is not None
                    target = _wait_aware_target(
                        scenario, queues, minute, wait_config
                    )
                else:
                    assert connectivity_config is not None
                    assert connectivity_vulnerability is not None
                    target = _connectivity_aware_target(
                        scenario,
                        queues,
                        minute,
                        connectivity_config,
                        connectivity_vulnerability,
                    )
                if target is None:
                    break
                _, line_id, stop_index = target
                line = line_by_id[line_id]
                target_stop = line.stops[stop_index]
                reposition = _reposition_minutes(
                    stop_graph,
                    reinforcement.location,
                    target_stop,
                )
                end_index = len(line.stops) - 1
                if policy == "dtpm-inspired":
                    short_end = choose_short_service_end(
                        scenario, dtpm_config, line_id, stop_index
                    )
                    if short_end is not None:
                        end_index = short_end
                        short_service_assignments += 1
                vehicle = Vehicle(
                    id=reinforcement.id,
                    line_id=line_id,
                    capacity=scenario.bus_capacity,
                )
                events[minute + reposition].append(
                    (vehicle, stop_index, reinforcement.id, end_index)
                )
                reinforcement.available = False
                reinforcement.assignments += 1
                reinforcement.reposition_minutes += reposition

        for vehicle, stop_index, reinforcement_id, end_index in list(events.get(minute, [])):
            line = line_by_id[vehicle.line_id]
            stop = line.stops[stop_index]
            arrivals_history[(line.id, stop)].append(minute)
            if reinforcement_id is None:
                regular_last_arrival[(line.id, stop)] = minute

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
                if passenger.line_id == line.id
                and passenger.arrival_minute <= minute
                and line.stops.index(passenger.destination) <= end_index
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

            if stop_index < end_index:
                events[minute + _segment_travel_minutes(scenario, line, stop_index)].append(
                    (vehicle, stop_index + 1, reinforcement_id, end_index)
                )
            elif reinforcement_id is not None:
                reinforcement = next(
                    item for item in reinforcements if item.id == reinforcement_id
                )
                reinforcement.location = stop
                reinforcement.available = True

    headways: list[int] = []
    for arrivals in arrivals_history.values():
        headways.extend(second - first for first, second in zip(arrivals, arrivals[1:]))

    boarded_count = sum(passenger.boarded_minute is not None for passenger in passengers)
    censored_wait_times = [
        (
            passenger.boarded_minute - passenger.arrival_minute
            if passenger.boarded_minute is not None
            else final_event_minute - passenger.arrival_minute
        )
        for passenger in passengers
    ]
    metrics = summarize_metrics(
        wait_times=wait_times,
        left_behind_count=sum(passenger.left_behind for passenger in passengers),
        load_factors=load_factors,
        observed_headways=headways,
        generated_passengers=len(passengers),
        boarded_passengers=boarded_count,
        censored_wait_times=censored_wait_times,
    )
    total_assignments = sum(item.assignments for item in reinforcements)
    total_reposition_minutes = sum(item.reposition_minutes for item in reinforcements)
    metadata: dict[str, object] = {
        "policy": policy,
        "seed": seed,
        "scenario_version": scenario.version,
        "duration_minutes": scenario.duration_minutes,
        "bus_capacity": scenario.bus_capacity,
        "regular_lines": len(scenario.lines),
        "reinforcement_buses": reinforcement_buses,
        "reinforcement_assignments": total_assignments,
        "reinforcement_reposition_minutes": total_reposition_minutes,
    }
    if dtpm_config is not None:
        metadata["policy_version"] = dtpm_config.version
        metadata["short_service_assignments"] = short_service_assignments
    if wait_config is not None:
        metadata["policy_version"] = wait_config.version
    if connectivity_config is not None:
        metadata["policy_version"] = connectivity_config.version
        metadata["vulnerability_model"] = connectivity_config.vulnerability_model
    return SimulationResult(metadata=metadata, metrics=metrics)


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
    best = max(candidates, key=lambda item: (item[0], item[1], -item[2]))
    return best if best[0] > 0 else None


def _dtpm_target(
    scenario: Scenario,
    queues: dict[str, list[Passenger]],
    minute: int,
    regular_last_arrival: dict[tuple[str, str], int],
    config: object,
) -> tuple[int, str, int] | None:
    candidates: list[tuple[int, str, int]] = []
    for line in scenario.lines:
        threshold = max(
            line.headway_minutes + config.absolute_extra_minutes,
            int(line.headway_minutes * config.multiple_of_scheduled),
        )
        crowd_threshold = scenario.bus_capacity * config.capacity_multiplier
        for stop_index, stop in enumerate(line.stops[:-1]):
            queue_size = sum(
                passenger.line_id == line.id and passenger.arrival_minute <= minute
                for passenger in queues[stop]
            )
            last_arrival = regular_last_arrival.get((line.id, stop))
            gap = minute if last_arrival is None else minute - last_arrival
            headway_trigger = gap > threshold and queue_size > 0
            crowding_trigger = queue_size > crowd_threshold
            if headway_trigger or crowding_trigger:
                severity = max(queue_size, int(gap - threshold) + queue_size)
                candidates.append((severity, line.id, stop_index))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], item[1], -item[2]))


def _wait_aware_target(
    scenario: Scenario,
    queues: dict[str, list[Passenger]],
    minute: int,
    config: object,
) -> tuple[int, str, int] | None:
    candidates: list[tuple[float, str, int]] = []
    for line in scenario.lines:
        for stop_index, stop in enumerate(line.stops[:-1]):
            eligible = [
                passenger
                for passenger in queues[stop]
                if passenger.line_id == line.id and passenger.arrival_minute <= minute
            ]
            if len(eligible) < config.minimum_queue:
                continue
            wait_burden = sum(minute - passenger.arrival_minute for passenger in eligible)
            capacity_risk = max(0, len(eligible) - scenario.bus_capacity)
            score = (
                wait_burden * config.wait_burden_weight
                + capacity_risk * config.capacity_risk_weight
            )
            candidates.append((score, line.id, stop_index))
    if not candidates:
        return None
    score, line_id, stop_index = max(
        candidates, key=lambda item: (item[0], item[1], -item[2])
    )
    return int(round(score)), line_id, stop_index


def _connectivity_aware_target(
    scenario: Scenario,
    queues: dict[str, list[Passenger]],
    minute: int,
    config: object,
    vulnerability: dict[str, float],
) -> tuple[int, str, int] | None:
    candidates: list[tuple[float, str, int]] = []
    for line in scenario.lines:
        for stop_index, stop in enumerate(line.stops[:-1]):
            eligible = [
                passenger
                for passenger in queues[stop]
                if passenger.line_id == line.id and passenger.arrival_minute <= minute
            ]
            if len(eligible) < config.minimum_queue:
                continue
            wait_burden = sum(minute - passenger.arrival_minute for passenger in eligible)
            capacity_risk = max(0, len(eligible) - scenario.bus_capacity)
            connectivity_term = vulnerability[stop] * len(eligible)
            score = (
                wait_burden * config.wait_burden_weight
                + capacity_risk * config.capacity_risk_weight
                + connectivity_term * config.connectivity_vulnerability_weight
            )
            candidates.append((score, line.id, stop_index))
    if not candidates:
        return None
    score, line_id, stop_index = max(
        candidates, key=lambda item: (item[0], item[1], -item[2])
    )
    return int(round(score)), line_id, stop_index


def _segment_travel_minutes(scenario: Scenario, line: object, stop_index: int) -> int:
    segment_times = getattr(line, "segment_travel_minutes", None)
    if segment_times is None:
        return scenario.travel_time_minutes
    return int(segment_times[stop_index])


def _build_stop_graph(scenario: Scenario) -> dict[str, dict[str, int]]:
    graph: dict[str, dict[str, int]] = {stop: {} for stop in scenario.stops}
    for line in scenario.lines:
        for index, (first, second) in enumerate(zip(line.stops, line.stops[1:])):
            weight = _segment_travel_minutes(scenario, line, index)
            previous = graph[first].get(second)
            if previous is None or weight < previous:
                graph[first][second] = weight
                graph[second][first] = weight
    return graph


def _reposition_minutes(
    graph: dict[str, dict[str, int]], origin: str, destination: str
) -> int:
    if origin == destination:
        return 0
    queue: list[tuple[int, str]] = [(0, origin)]
    best = {origin: 0}
    while queue:
        minutes, stop = heapq.heappop(queue)
        if stop == destination:
            return minutes
        if minutes != best.get(stop):
            continue
        for neighbour, weight in sorted(graph[stop].items()):
            candidate = minutes + weight
            if candidate >= best.get(neighbour, 10**9):
                continue
            best[neighbour] = candidate
            heapq.heappush(queue, (candidate, neighbour))
    raise ValueError(f"No reposition path from {origin} to {destination}")
