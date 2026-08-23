from __future__ import annotations

import argparse
import json
from pathlib import Path

from buscomodin.m7data import (
    download_source,
    kmz_to_geojson,
    load_source_manifest,
    write_provenance,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and normalize versioned M7 public data sources")
    parser.add_argument("source_id")
    parser.add_argument("--output-dir", default="data/m7")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = load_source_manifest()
    source = next((item for item in manifest["sources"] if item["id"] == args.source_id), None)
    if source is None:
        raise SystemExit(f"Unknown source_id: {args.source_id}")
    print(json.dumps(source, indent=2, ensure_ascii=False, sort_keys=True))
    if args.dry_run:
        return 0
    target, checksum = download_source(source, args.output_dir)
    provenance_path = Path(args.output_dir) / f"{args.source_id}.provenance.json"
    write_provenance(source, target, checksum, provenance_path)
    print(f"Downloaded: {target}")
    print(f"SHA256: {checksum}")
    print(f"Provenance: {provenance_path}")
    if source["kind"] == "kmz":
        services = tuple(source.get("target_services", []))
        geojson = kmz_to_geojson(target, services)
        geojson_path = Path(args.output_dir) / f"{args.source_id}.geojson"
        geojson_path.write_text(
            json.dumps(geojson, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        print(f"GeoJSON: {geojson_path} ({len(geojson['features'])} features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
