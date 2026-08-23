import json
from pathlib import Path

from buscomodin.scenario import load_scenario


SCENARIO = Path("configs/scenario-villa-alemana-real-am-v1.json")
PROVENANCE = Path("data/reference/m7/scenario-villa-alemana-real-am-v1.provenance.json")


def test_m7_real_network_scenario_is_core_compatible() -> None:
    scenario = load_scenario(SCENARIO)
    assert scenario.version == "villa-alemana-real-network-am-v1"
    assert scenario.duration_minutes == 60
    assert len(scenario.lines) == 9
    assert len(scenario.stops) >= 100
    assert len(scenario.hubs) == 2


def test_m7_am_headways_come_from_un11_program() -> None:
    scenario = load_scenario(SCENARIO)
    headways = {line.id: line.headway_minutes for line in scenario.lines}
    assert headways["C01_I"] == 15
    assert headways["C01_R"] == 15
    assert headways["C02_I"] == 15
    assert headways["C02_R"] == 15
    assert headways["C03_I"] == 15
    assert headways["C03_R"] == 15
    assert headways["C03Y_I"] == 60
    assert "C03Y_R" not in headways
    assert headways["C04_I"] == 30
    assert headways["C04_R"] == 30


def test_m7_provenance_marks_remaining_estimates() -> None:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert "DTPR DSL4654 UN11 KMZ" in provenance["route_source"]
    assert "Anexo N°3" in provenance["frequency_source"]
    assert provenance["demand_status"] == "synthetic-not-calibrated"
    assert provenance["capacity_status"].startswith("estimated")
    assert provenance["travel_time_status"].startswith("modeled")
