from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_VILLA_ALEMANA_GEO_PATH = (
    Path(__file__).resolve().parents[2] / "configs" / "villa-alemana-geo-v1.json"
)


@dataclass(frozen=True)
class GeoAnchor:
    id: str
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class GeoConfig:
    version: str
    west: float
    south: float
    east: float
    north: float
    anchors: tuple[GeoAnchor, ...]
    osm_file: str
    network_file: str
    vehicle_classes: str

    @property
    def bbox_string(self) -> str:
        return f"{self.west},{self.south},{self.east},{self.north}"


def load_villa_alemana_geo(path: str | Path | None = None) -> GeoConfig:
    config_path = Path(path) if path else DEFAULT_VILLA_ALEMANA_GEO_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    bbox = raw["bbox"]
    sumo = raw["sumo"]
    return GeoConfig(
        version=raw["version"],
        west=float(bbox["west"]),
        south=float(bbox["south"]),
        east=float(bbox["east"]),
        north=float(bbox["north"]),
        anchors=tuple(GeoAnchor(**anchor) for anchor in raw["anchors"]),
        osm_file=sumo["osm_file"],
        network_file=sumo["network_file"],
        vehicle_classes=sumo["vehicle_classes"],
    )


def sumo_import_commands(config: GeoConfig, sumo_home: str | Path, output_dir: str | Path) -> tuple[list[str], list[str]]:
    tools = Path(sumo_home) / "tools"
    output = Path(output_dir)
    osm_path = output / config.osm_file
    get_command = [
        "python",
        str(tools / "osmGet.py"),
        "--bbox",
        config.bbox_string,
        "--prefix",
        str(output / "villa-alemana"),
    ]
    build_command = [
        "python",
        str(tools / "osmBuild.py"),
        "--osm-file",
        str(osm_path),
        "--vehicle-classes",
        config.vehicle_classes,
        "--output-directory",
        str(output),
        "--prefix",
        "villa-alemana",
    ]
    return get_command, build_command
