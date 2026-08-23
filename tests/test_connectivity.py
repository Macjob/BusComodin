from buscomodin.connectivity import (
    load_connectivity_policy,
    regular_line_count_by_stop,
    vulnerability_by_stop,
)
from buscomodin.scenario import load_scenario
from buscomodin.simulation import (
    run_baseline,
    run_connectivity_aware,
    run_dtpm_inspired,
    run_queue_first,
    run_wait_aware,
)


def test_connectivity_policy_is_versioned() -> None:
    config = load_connectivity_policy()
    assert config.version == "connectivity-aware-v1"
    assert config.vulnerability_model == "inverse_regular_line_count"
    assert config.connectivity_vulnerability_weight == 120.0


def test_vulnerability_rewards_stops_with_fewer_alternatives() -> None:
    scenario = load_scenario()
    counts = regular_line_count_by_stop(scenario)
    vulnerability = vulnerability_by_stop(scenario)
    assert counts["S01"] == 1
    assert counts["S08"] == 2
    assert vulnerability["S01"] > vulnerability["S08"]


def test_connectivity_aware_is_deterministic_and_comparable() -> None:
    scenario = load_scenario()
    first = run_connectivity_aware(scenario, seed=42).to_dict()
    second = run_connectivity_aware(scenario, seed=42).to_dict()
    results = [
        run_baseline(scenario, 42).to_dict(),
        run_queue_first(scenario, 42).to_dict(),
        run_dtpm_inspired(scenario, 42).to_dict(),
        run_wait_aware(scenario, 42).to_dict(),
    ]
    assert first == second
    assert first["metadata"]["policy_version"] == "connectivity-aware-v1"
    generated = first["metrics"]["generated_passengers"]
    assert all(item["metrics"]["generated_passengers"] == generated for item in results)
