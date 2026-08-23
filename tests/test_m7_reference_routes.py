import json
from pathlib import Path


REFERENCE_ROUTES = Path("data/reference/m7/elc0004-services-120-122-125.geojson")
REFERENCE_PROVENANCE = Path("data/reference/m7/elc0004-services-120-122-125.provenance.json")


def test_tracked_reference_routes_are_exactly_target_services() -> None:
    payload = json.loads(REFERENCE_ROUTES.read_text(encoding="utf-8"))
    names = {feature["properties"]["name"] for feature in payload["features"]}
    assert names == {"120_I", "120_R", "122_I", "122_R", "125 I", "125 R"}
    assert all(feature["geometry"]["type"] == "LineString" for feature in payload["features"])


def test_reference_routes_record_real_source_checksum() -> None:
    provenance = json.loads(REFERENCE_PROVENANCE.read_text(encoding="utf-8"))
    assert provenance["source_id"] == "dtpr-elc0004-routes-kmz"
    assert provenance["source_sha256"] == "b316bc44e29b0f7c8be4bf8d0d7c91d1cc7dac753481b81c75397af2ba30ff34"
    assert provenance["source_status"] == "official-reference-2022"
