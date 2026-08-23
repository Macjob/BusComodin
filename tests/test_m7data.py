import json
import zipfile
from pathlib import Path

from buscomodin.m7data import kmz_to_geojson, load_source_manifest, sha256_file, write_provenance


def test_m7_manifest_contains_official_route_source() -> None:
    manifest = load_source_manifest()
    assert manifest["version"] == "m7-data-sources-v1"
    source = next(item for item in manifest["sources"] if item["id"] == "dtpr-elc0004-routes-kmz")
    assert source["organization"] == "DTPR / MTT Chile"
    assert source["target_services"] == ["120", "122", "125"]
    assert "documentoId=19145139" in source["download_url"]


def test_kmz_to_geojson_filters_target_services(tmp_path: Path) -> None:
    kml = """<?xml version='1.0' encoding='UTF-8'?>
    <kml xmlns='http://www.opengis.net/kml/2.2'><Document>
      <Placemark><name>Servicio 120 ida</name><LineString><coordinates>-71.4,-33.04,0 -71.38,-33.04,0</coordinates></LineString></Placemark>
      <Placemark><name>Servicio 999</name><LineString><coordinates>-71.3,-33.03,0 -71.2,-33.02,0</coordinates></LineString></Placemark>
    </Document></kml>"""
    kmz = tmp_path / "routes.kmz"
    with zipfile.ZipFile(kmz, "w") as archive:
        archive.writestr("doc.kml", kml)
    geojson = kmz_to_geojson(kmz, ("120", "122", "125"))
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    assert geojson["features"][0]["properties"]["name"] == "Servicio 120 ida"


def test_provenance_records_checksum(tmp_path: Path) -> None:
    raw = tmp_path / "source.bin"
    raw.write_bytes(b"buscomodin")
    source = {
        "id": "source-test",
        "organization": "Test Org",
        "status": "test",
        "published_date": "2026-01-01",
        "landing_page": "https://example.test",
        "download_url": "https://example.test/file",
    }
    checksum = sha256_file(raw)
    target = write_provenance(source, raw, checksum, tmp_path / "provenance.json")
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["sha256"] == checksum
    assert payload["source_id"] == "source-test"
