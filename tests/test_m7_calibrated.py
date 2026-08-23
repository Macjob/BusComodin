import json
from pathlib import Path

from buscomodin.scenario import load_scenario


SCENARIO = Path("configs/scenario-villa-alemana-un11-2025-calibrated-v1.json")
PROVENANCE = Path("data/reference/m7/scenario-villa-alemana-un11-2025-calibrated-v1.provenance.json")


def test_calibrated_2025_scenario_is_separate_and_traceable() -> None:
    scenario = load_scenario(SCENARIO)
    assert scenario.version == "villa-alemana-un11-2025-calibrated-v1"
    assert scenario.travel_time_minutes == 1
    assert scenario.bus_capacity == 35
    assert scenario.demand.base_rate_per_stop_minute == 0.05
    assert scenario.demand.peak_multiplier == 2.0


def test_calibrated_2025_provenance_marks_uncertainty_and_2026_transition() -> None:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert provenance["demand_calibration"]["status"] == "historical-provisional"
    assert provenance["travel_time_calibration"]["status"] == "historical-provisional"
    assert provenance["capacity_calibration"]["status"] == "unconfirmed-sensitivity-required"
    assert "2026-01-31" in provenance["current_2026_status"]["warning"]
    assert "2026-02-02" in provenance["current_2026_status"]["warning"]
