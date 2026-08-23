from __future__ import annotations

import math
import random

from .models import Passenger, Scenario


def _poisson(rng: random.Random, rate: float) -> int:
    """Sample a Poisson distribution using Knuth's method."""
    if rate <= 0:
        return 0
    limit = math.exp(-rate)
    product = 1.0
    count = 0
    while product > limit:
        count += 1
        product *= rng.random()
    return count - 1


def generate_demand(scenario: Scenario, seed: int) -> list[Passenger]:
    """Generate deterministic passenger arrivals for a scenario and seed."""
    rng = random.Random(seed)
    services_by_stop: dict[str, list[tuple[str, tuple[str, ...], int]]] = {
        stop: [] for stop in scenario.stops
    }
    for line in scenario.lines:
        for index, stop in enumerate(line.stops[:-1]):
            services_by_stop[stop].append((line.id, line.stops, index))

    passengers: list[Passenger] = []
    passenger_id = 0
    for minute in range(scenario.duration_minutes):
        peak = scenario.demand.peak_start_minute <= minute < scenario.demand.peak_end_minute
        for stop in scenario.stops:
            services = services_by_stop[stop]
            if not services:
                continue
            rate = scenario.demand.base_rate_per_stop_minute
            if peak:
                rate *= scenario.demand.peak_multiplier
            if stop in scenario.hubs:
                rate *= scenario.demand.hub_origin_multiplier

            for _ in range(_poisson(rng, rate)):
                line_id, line_stops, origin_index = rng.choice(services)
                destination = rng.choice(line_stops[origin_index + 1 :])
                passengers.append(
                    Passenger(
                        id=passenger_id,
                        arrival_minute=minute,
                        origin=stop,
                        destination=destination,
                        line_id=line_id,
                    )
                )
                passenger_id += 1
    return passengers
