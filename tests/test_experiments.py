from buscomodin.experiments import load_experiment_config, vary_scenario
from buscomodin.scenario import load_scenario


def test_m5_config_is_versioned_and_multi_seed() -> None:
    config = load_experiment_config()
    assert config["version"] == "m5-v1"
    assert len(config["seeds"]) == 20
    assert config["reinforcement_buses"] == [1, 2, 3, 4, 5]


def test_sensitivity_variations_do_not_mutate_base() -> None:
    base = load_scenario()
    demand = vary_scenario(base, "demand_multiplier", 1.5)
    capacity = vary_scenario(base, "capacity_multiplier", 0.75)
    headway = vary_scenario(base, "headway_multiplier", 1.5)
    congestion = vary_scenario(base, "congestion_multiplier", 1.5)
    failure = vary_scenario(base, "partial_line_failure", "L2")

    assert demand.demand.base_rate_per_stop_minute > base.demand.base_rate_per_stop_minute
    assert capacity.bus_capacity < base.bus_capacity
    assert headway.lines[0].headway_minutes > base.lines[0].headway_minutes
    assert congestion.travel_time_minutes > base.travel_time_minutes
    assert failure.lines[1].headway_minutes == base.lines[1].headway_minutes * 2
    assert base.bus_capacity == 35
