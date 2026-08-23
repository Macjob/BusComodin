import json
from pathlib import Path

from buscomodin.scenario import load_scenario


SCENARIO = Path("configs/scenario-villa-alemana-un11-2025-spatial-v1.json")
PROVENANCE = Path("data/reference/m7/scenario-villa-alemana-un11-2025-spatial-v1.provenance.json")


def test_spatial_scenario_has_segment_times_for_every_line() -> None:
    scenario = load_scenario(SCENARIO)
    assert scenario.version == "villa-alemana-un11-2025-spatial-v1"
    assert len(scenario.stops) == 79
    for line in scenario.lines:
        assert line.segment_travel_minutes is not None
        assert len(line.segment_travel_minutes) == len(line.stops) - 1
        assert all(value >= 1 for value in line.segment_travel_minutes)


def test_spatial_provenance_uses_sectra_speed_and_marks_sumo_pending() -> None:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert provenance["commercial_speed_kmh"] == 30.0
    assert provenance["timing_status"] == "spatial-provisional-pending-SUMO"
    assert provenance["new_unique_stops"] == 79
