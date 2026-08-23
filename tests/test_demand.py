from buscomodin.demand import generate_demand
from buscomodin.scenario import load_scenario


def test_demand_is_deterministic_for_same_seed() -> None:
    scenario = load_scenario()
    first = generate_demand(scenario, seed=42)
    second = generate_demand(scenario, seed=42)
    assert first == second
    assert len(first) > 0


def test_different_seed_changes_demand() -> None:
    scenario = load_scenario()
    first = generate_demand(scenario, seed=42)
    second = generate_demand(scenario, seed=43)
    assert first != second
