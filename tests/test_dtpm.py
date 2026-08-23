from buscomodin.dtpm import choose_short_service_end, load_dtpm_policy
from buscomodin.scenario import load_scenario
from buscomodin.simulation import run_baseline, run_dtpm_inspired, run_queue_first


def test_dtpm_policy_config_is_versioned() -> None:
    config = load_dtpm_policy()
    assert config.version == "dtpm-inspired-v1"
    assert config.absolute_extra_minutes == 15
    assert config.multiple_of_scheduled == 2.0
    assert config.capacity_multiplier == 1.2
    assert config.short_services


def test_short_service_catalog_is_executable() -> None:
    scenario = load_scenario()
    config = load_dtpm_policy()
    line = next(line for line in scenario.lines if line.id == "L2")
    start_index = line.stops.index("S08")
    end_index = choose_short_service_end(scenario, config, "L2", start_index)
    assert end_index == line.stops.index("S16")


def test_dtpm_inspired_is_deterministic_and_comparable() -> None:
    scenario = load_scenario()
    first = run_dtpm_inspired(scenario, seed=42).to_dict()
    second = run_dtpm_inspired(scenario, seed=42).to_dict()
    baseline = run_baseline(scenario, seed=42).to_dict()
    queue_first = run_queue_first(scenario, seed=42).to_dict()

    assert first == second
    assert first["metadata"]["reinforcement_buses"] == 3
    assert first["metadata"]["policy_version"] == "dtpm-inspired-v1"
    assert first["metrics"]["generated_passengers"] == baseline["metrics"]["generated_passengers"]
    assert first["metrics"]["generated_passengers"] == queue_first["metrics"]["generated_passengers"]
