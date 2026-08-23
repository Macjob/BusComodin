from __future__ import annotations

import json
import math
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}
ROUTE_NAME_MAP = {
    "C01 IDA": "C01_I",
    "C01 REGRESO": "C01_R",
    "C02": "C02_I",
    "C02 REGRESO": "C02_R",
    "C03 IDA": "C03_I",
    "C03 REGRESO": "C03_R",
    "C03Y IDA": "C03Y_I",
    "C03Y REGRESO": "C03Y_R",
    "C04 IDA": "C04_I",
    "C04 REGRESO": "C04_R",
}
AM_HEADWAYS = {
    "C01_I": 15,
    "C01_R": 15,
    "C02_I": 15,
    "C02_R": 15,
    "C03_I": 15,
    "C03_R": 15,
    "C03Y_I": 60,
    "C04_I": 30,
    "C04_R": 30,
}


def _xy(lon: float, lat: float, lat0: float) -> tuple[float, float]:
    return lon * 111_320.0 * math.cos(math.radians(lat0)), lat * 110_540.0


def _project_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> tuple[float, float]:
    vx, vy = bx - ax, by - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return math.hypot(px - ax, py - ay), 0.0
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / denom))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy), t


def _route_projection(point: tuple[float, float], coords: list[list[float]]) -> tuple[float, float]:
    lat0 = sum(c[1] for c in coords) / len(coords)
    px, py = _xy(point[0], point[1], lat0)
    xy = [_xy(c[0], c[1], lat0) for c in coords]
    cumulative = [0.0]
    for a, b in zip(xy, xy[1:]):
        cumulative.append(cumulative[-1] + math.dist(a, b))
    best_distance = float("inf")
    best_along = 0.0
    for index, (a, b) in enumerate(zip(xy, xy[1:])):
        distance, t = _project_to_segment(px, py, a[0], a[1], b[0], b[1])
        if distance < best_distance:
            best_distance = distance
            best_along = cumulative[index] + t * math.dist(a, b)
    return best_distance, best_along


def load_routes(kmz_path: Path) -> dict[str, list[list[float]]]:
    with zipfile.ZipFile(kmz_path) as archive:
        kml_name = next(name for name in archive.namelist() if name.lower().endswith(".kml"))
        root = ET.fromstring(archive.read(kml_name))
    routes: dict[str, list[list[float]]] = {}
    for placemark in root.findall(".//kml:Placemark", KML_NS):
        name = (placemark.findtext("kml:name", default="", namespaces=KML_NS) or "").strip()
        route_id = ROUTE_NAME_MAP.get(name)
        if not route_id:
            continue
        raw = placemark.findtext(".//kml:LineString/kml:coordinates", default="", namespaces=KML_NS)
        coords = []
        for token in raw.split():
            parts = token.split(",")
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])
        routes[route_id] = coords
    return routes


def load_osm_stops(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    seen: set[int] = set()
    stops = []
    for element in payload["elements"]:
        node_id = int(element["id"])
        if node_id in seen:
            continue
        seen.add(node_id)
        tags = element.get("tags", {})
        stops.append({
            "id": f"OSM_{node_id}",
            "osm_id": node_id,
            "name": tags.get("name") or tags.get("ref") or f"OSM {node_id}",
            "lat": float(element["lat"]),
            "lon": float(element["lon"]),
        })
    return stops


def match_stops(routes: dict[str, list[list[float]]], stops: list[dict[str, object]], threshold_m: float = 120.0) -> dict[str, list[dict[str, object]]]:
    matched: dict[str, list[dict[str, object]]] = {}
    for route_id, coords in routes.items():
        candidates = []
        for stop in stops:
            distance, along = _route_projection((float(stop["lon"]), float(stop["lat"])), coords)
            if distance <= threshold_m:
                candidates.append({**stop, "distance_to_route_m": round(distance, 1), "along_route_m": round(along, 1)})
        candidates.sort(key=lambda item: float(item["along_route_m"]))
        deduped = []
        for candidate in candidates:
            if deduped and abs(float(candidate["along_route_m"]) - float(deduped[-1]["along_route_m"])) < 35.0:
                if float(candidate["distance_to_route_m"]) < float(deduped[-1]["distance_to_route_m"]):
                    deduped[-1] = candidate
                continue
            deduped.append(candidate)
        matched[route_id] = deduped
    return matched


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    kmz = repo / "data" / "m7" / "un11-services-2024.kmz"
    osm = repo / "data" / "m7" / "osm-stops-un11.json"
    routes = load_routes(kmz)
    stops = load_osm_stops(osm)
    matched = match_stops(routes, stops)

    active_routes = {route_id: seq for route_id, seq in matched.items() if route_id in AM_HEADWAYS and len(seq) >= 2}
    all_stop_ids = sorted({stop["id"] for seq in active_routes.values() for stop in seq})
    stop_lookup = {stop["id"]: stop for seq in active_routes.values() for stop in seq}
    hubs = []
    for preferred in ("C01_I", "C02_I", "C04_I"):
        seq = active_routes.get(preferred, [])
        if seq:
            hubs.append(seq[0]["id"])
        if len(hubs) == 2:
            break

    scenario = {
        "version": "villa-alemana-real-network-am-v1",
        "duration_minutes": 60,
        "travel_time_minutes": 2,
        "bus_capacity": 35,
        "hubs": hubs,
        "stops": all_stop_ids,
        "lines": [
            {"id": route_id, "headway_minutes": AM_HEADWAYS[route_id], "stops": [stop["id"] for stop in seq]}
            for route_id, seq in sorted(active_routes.items())
        ],
        "demand": {
            "base_rate_per_stop_minute": 0.10,
            "peak_start_minute": 0,
            "peak_end_minute": 60,
            "peak_multiplier": 2.0,
            "hub_origin_multiplier": 1.25,
        },
    }
    reference_dir = repo / "data" / "reference" / "m7"
    reference_dir.mkdir(parents=True, exist_ok=True)
    (reference_dir / "un11-osm-stops-matched-v1.json").write_text(json.dumps(matched, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (reference_dir / "un11-osm-stop-catalog-v1.json").write_text(json.dumps({sid: stop_lookup[sid] for sid in all_stop_ids}, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    config_dir = repo / "configs"
    (config_dir / "scenario-villa-alemana-real-am-v1.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    summary = {
        "scenario_version": scenario["version"],
        "route_count": len(active_routes),
        "unique_stops": len(all_stop_ids),
        "routes": {route_id: {"headway_minutes": AM_HEADWAYS[route_id], "matched_stops": len(seq)} for route_id, seq in sorted(active_routes.items())},
        "route_source": "DTPR DSL4654 UN11 KMZ, documentoId=21963290, published 2024-10-22",
        "frequency_source": "DTPR DSL4654 UN11 Bases, Anexo N°3, documentoId=21963165; laboral 08:00-08:59",
        "stop_source": "OpenStreetMap nodes highway=bus_stop or public_transport=platform, matched <=120 m to official DTPR shapes",
        "demand_status": "synthetic-not-calibrated",
        "capacity_status": "estimated-35-until-fleet-capacity-is-materialized",
        "travel_time_status": "modeled-2-min-per-stop-until-SUMO-network-is-materialized",
    }
    (reference_dir / "scenario-villa-alemana-real-am-v1.provenance.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
