from __future__ import annotations

import argparse
import json
from pathlib import Path

from buscomodin.m7data import kmz_to_geojson, load_source_manifest, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Build tracked M7 reference routes from the downloaded DTPR KMZ")
    parser.add_argument("--kmz", default="data/m7/elc0004-routes.kmz")
    parser.add_argument("--output-dir", default="data/reference/m7")
    args = parser.parse_args()

    manifest = load_source_manifest()
    source = next(item for item in manifest["sources"] if item["id"] == "dtpr-elc0004-routes-kmz")
    kmz_path = Path(args.kmz)
    checksum = sha256_file(kmz_path)
    services = tuple(source["target_services"])
    geojson = kmz_to_geojson(kmz_path, services)

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    routes_path = output / "elc0004-services-120-122-125.geojson"
    routes_path.write_text(
        json.dumps(geojson, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    names = [feature["properties"]["name"] for feature in geojson["features"]]
    provenance = {
        "artifact": routes_path.name,
        "source_id": source["id"],
        "organization": source["organization"],
        "source_status": source["status"],
        "source_published_date": source["published_date"],
        "landing_page": source["landing_page"],
        "download_url": source["download_url"],
        "source_filename": source["filename"],
        "source_sha256": checksum,
        "target_services": list(services),
        "features": names,
        "transformation": "Extract LineString Placemarks whose names contain 120, 122 or 125; preserve WGS84 lon/lat coordinates.",
    }
    provenance_path = output / "elc0004-services-120-122-125.provenance.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Routes: {routes_path} ({len(names)} features)")
    print(f"Provenance: {provenance_path}")
    print(f"Source SHA256: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
