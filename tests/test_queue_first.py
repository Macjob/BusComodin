from buscomodin.scenario import load_scenario
from buscomodin.simulation import run_baseline, run_queue_first


def test_queue_first_is_deterministic_and_uses_three_reinforcements() -> None:
    scenario = load_scenario()
    first = run_queue_first(scenario, seed=42).to_dict()
    second = run_queue_first(scenario, seed=42).to_dict()
    assert first == second
    assert first["metadata"]["reinforcement_buses"] == 3
    assert first["metadata"]["reinforcements_dispatched"] == 3


def test_queue_first_uses_same_demand_as_baseline() -> None:
    scenario = load_scenario()
    baseline = run_baseline(scenario, seed=42).to_dict()
    queue_first = run_queue_first(scenario, seed=42).to_dict()
    assert baseline["metadata"]["scenario_version"] == queue_first["metadata"]["scenario_version"]
    assert baseline["metrics"]["generated_passengers"] == queue_first["metrics"]["generated_passengers"]
