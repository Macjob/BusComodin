from __future__ import annotations

import json
from pathlib import Path

COMMERCIAL_SPEED_KMH = 30.0
METERS_PER_MINUTE = COMMERCIAL_SPEED_KMH * 1000.0 / 60.0


def sample_route(stops: list[dict[str, object]]) -> list[dict[str, object]]:
    if len(stops) <= 2:
        return stops
    selected = [stops[0]]
    next_target = float(stops[0]["along_route_m"]) + METERS_PER_MINUTE
    for stop in stops[1:-1]:
        along = float(stop["along_route_m"])
        if along >= next_target:
            selected.append(stop)
            next_target = along + METERS_PER_MINUTE
    if selected[-1]["id"] != stops[-1]["id"]:
        selected.append(stops[-1])
    return selected


def segment_minutes(stops: list[dict[str, object]]) -> list[int]:
    values = []
    for first, second in zip(stops, stops[1:]):
        distance = max(1.0, float(second["along_route_m"]) - float(first["along_route_m"]))
        values.append(max(1, round(distance / METERS_PER_MINUTE)))
    return values


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source = repo / "configs" / "scenario-villa-alemana-un11-2025-calibrated-v1.json"
    matched_path = repo / "data" / "reference" / "m7" / "un11-osm-stops-matched-v1.json"
    target = repo / "configs" / "scenario-villa-alemana-un11-2025-spatial-v1.json"
    provenance_path = repo / "data" / "reference" / "m7" / "scenario-villa-alemana-un11-2025-spatial-v1.provenance.json"

    scenario = json.loads(source.read_text(encoding="utf-8"))
    matched = json.loads(matched_path.read_text(encoding="utf-8"))
    old_stop_count = len(scenario["stops"])

    new_lines = []
    stop_ids: set[str] = set()
    route_summary = {}
    for line in scenario["lines"]:
        route_id = line["id"]
        sampled = sample_route(matched[route_id])
        times = segment_minutes(sampled)
        ids = [str(stop["id"]) for stop in sampled]
        stop_ids.update(ids)
        new_lines.append({
            "id": route_id,
            "headway_minutes": line["headway_minutes"],
            "stops": ids,
            "segment_travel_minutes": times,
        })
        route_summary[route_id] = {
            "matched_stops_before": len(matched[route_id]),
            "sampled_stops": len(ids),
            "modeled_runtime_minutes": sum(times),
            "projected_length_km": round((float(sampled[-1]["along_route_m"]) - float(sampled[0]["along_route_m"])) / 1000.0, 3),
        }

    new_stop_count = len(stop_ids)
    scenario["version"] = "villa-alemana-un11-2025-spatial-v1"
    scenario["lines"] = new_lines
    scenario["stops"] = sorted(stop_ids)
    scenario["hubs"] = [new_lines[0]["stops"][0], new_lines[2]["stops"][0]]
    scenario["travel_time_minutes"] = 1  # legacy fallback; every M7 line now has segment times
    # Preserve the benchmark's approximate total arrival intensity while reducing map-matched stop density.
    scenario["demand"]["base_rate_per_stop_minute"] = round(
        float(scenario["demand"]["base_rate_per_stop_minute"]) * old_stop_count / new_stop_count,
        8,
    )
    target.write_text(json.dumps(scenario, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    provenance = {
        "scenario_version": scenario["version"],
        "parent_scenario": "villa-alemana-un11-2025-calibrated-v1",
        "timing_status": "spatial-provisional-pending-SUMO",
        "commercial_speed_kmh": COMMERCIAL_SPEED_KMH,
        "commercial_speed_source": "SECTRA PMTP Gran Valparaiso: average bus speed ~30 km/h in punta manana",
        "method": "Sample OSM-matched stops at approximately one commercial-speed minute (~500 m) along each official DTPR shape; derive integer segment times from along-shape distance.",
        "old_unique_stops": old_stop_count,
        "new_unique_stops": new_stop_count,
        "demand_preservation": "Base stop arrival rate scaled by old/new unique-stop ratio to isolate timing/topology-density change while keeping expected total benchmark demand approximately constant.",
        "demand_base_rate_per_stop_minute": scenario["demand"]["base_rate_per_stop_minute"],
        "routes": route_summary,
        "limitations": [
            "OSM stops are secondary map data, not an official UN11 stop list.",
            "Commercial speed is system-level historical evidence, not route-specific observed speed.",
            "SUMO road-network routing and intersection delays are not yet materialized.",
        ],
    }
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
