from buscomodin.scenario import load_scenario
from buscomodin.simulation import (
    run_baseline,
    run_dtpm_inspired,
    run_queue_first,
    run_wait_aware,
)
from buscomodin.waitaware import load_wait_aware_policy


def test_wait_aware_config_is_versioned() -> None:
    config = load_wait_aware_policy()
    assert config.version == "wait-aware-v1"
    assert config.wait_burden_weight == 1.0
    assert config.capacity_risk_weight == 8.0
    assert config.minimum_queue == 1


def test_wait_aware_is_deterministic_and_comparable() -> None:
    scenario = load_scenario()
    first = run_wait_aware(scenario, seed=42).to_dict()
    second = run_wait_aware(scenario, seed=42).to_dict()
    baseline = run_baseline(scenario, seed=42).to_dict()
    queue_first = run_queue_first(scenario, seed=42).to_dict()
    dtpm = run_dtpm_inspired(scenario, seed=42).to_dict()

    assert first == second
    assert first["metadata"]["reinforcement_buses"] == 3
    assert first["metadata"]["policy_version"] == "wait-aware-v1"
    expected = baseline["metrics"]["generated_passengers"]
    assert first["metrics"]["generated_passengers"] == expected
    assert queue_first["metrics"]["generated_passengers"] == expected
    assert dtpm["metrics"]["generated_passengers"] == expected
