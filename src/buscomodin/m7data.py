from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DEFAULT_SOURCE_MANIFEST = Path(__file__).resolve().parents[2] / "configs" / "data-sources-m7-v1.json"
KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def load_source_manifest(path: str | Path | None = None) -> dict[str, object]:
    manifest_path = Path(path) if path else DEFAULT_SOURCE_MANIFEST
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_source(source: dict[str, object], output_dir: str | Path) -> tuple[Path, str]:
    url = source.get("download_url")
    filename = source.get("filename")
    if not url or not filename:
        raise ValueError(f"Source {source.get('id')} is not directly downloadable")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    target = output / str(filename)
    request = urllib.request.Request(str(url), headers={"User-Agent": "BusComodin/0.1 research"})
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)
    return target, sha256_file(target)


def kmz_to_geojson(kmz_path: str | Path, target_services: tuple[str, ...] = ()) -> dict[str, object]:
    with zipfile.ZipFile(kmz_path) as archive:
        kml_names = [name for name in archive.namelist() if name.lower().endswith(".kml")]
        if not kml_names:
            raise ValueError("KMZ does not contain KML")
        root = ET.fromstring(archive.read(kml_names[0]))

    features: list[dict[str, object]] = []
    for placemark in root.findall(".//kml:Placemark", KML_NS):
        name = (placemark.findtext("kml:name", default="", namespaces=KML_NS) or "").strip()
        if target_services and not any(service in name for service in target_services):
            continue
        coordinates = placemark.findtext(".//kml:LineString/kml:coordinates", default="", namespaces=KML_NS)
        if not coordinates:
            continue
        points = []
        for token in coordinates.split():
            parts = token.split(",")
            if len(parts) >= 2:
                points.append([float(parts[0]), float(parts[1])])
        if len(points) < 2:
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {"name": name},
                "geometry": {"type": "LineString", "coordinates": points},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def write_provenance(source: dict[str, object], file_path: str | Path, checksum: str, output_path: str | Path) -> Path:
    provenance = {
        "source_id": source["id"],
        "organization": source["organization"],
        "status": source["status"],
        "published_date": source["published_date"],
        "landing_page": source["landing_page"],
        "download_url": source.get("download_url"),
        "filename": Path(file_path).name,
        "sha256": checksum,
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(provenance, indent=2, sort_keys=True), encoding="utf-8")
    return target
