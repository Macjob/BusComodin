from __future__ import annotations

import math
from statistics import fmean
from typing import Iterable


def percentile(values: Iterable[float], percentile_value: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile_value
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize_metrics(
    wait_times: list[int],
    left_behind_count: int,
    load_factors: list[float],
    observed_headways: list[int],
    generated_passengers: int,
    boarded_passengers: int,
) -> dict[str, float | int]:
    return {
        "generated_passengers": generated_passengers,
        "boarded_passengers": boarded_passengers,
        "mean_wait_minutes": round(fmean(wait_times), 4) if wait_times else 0.0,
        "p95_wait_minutes": round(percentile(wait_times, 0.95), 4),
        "passengers_left_behind": left_behind_count,
        "mean_load_factor": round(fmean(load_factors), 4) if load_factors else 0.0,
        "max_load_factor": round(max(load_factors), 4) if load_factors else 0.0,
        "mean_observed_headway_minutes": round(fmean(observed_headways), 4)
        if observed_headways
        else 0.0,
        "p95_observed_headway_minutes": round(percentile(observed_headways, 0.95), 4),
    }
