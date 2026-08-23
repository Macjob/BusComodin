from buscomodin.scenario import load_scenario
from buscomodin.simulation import run_baseline


def test_synthetic_scenario_matches_m0_scope() -> None:
    scenario = load_scenario()
    assert 20 <= len(scenario.stops) <= 30
    assert len(scenario.lines) == 3
    assert len(scenario.hubs) == 2
    assert scenario.bus_capacity > 0


def test_baseline_is_deterministic() -> None:
    scenario = load_scenario()
    first = run_baseline(scenario, seed=42).to_dict()
    second = run_baseline(scenario, seed=42).to_dict()
    assert first == second
    assert first["metadata"]["reinforcement_buses"] == 0
