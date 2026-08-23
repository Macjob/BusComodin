from pathlib import Path

from buscomodin.geography import load_villa_alemana_geo, sumo_import_commands
from buscomodin.scenario import load_scenario


def test_villa_alemana_geo_has_five_real_station_anchors() -> None:
    config = load_villa_alemana_geo()
    names = {anchor.name for anchor in config.anchors}
    assert config.version == "villa-alemana-geo-v1"
    assert names == {
        "Las Américas",
        "La Concepción",
        "Villa Alemana",
        "Sargento Aldea",
        "Peñablanca",
    }
    assert config.west < config.east
    assert config.south < config.north


def test_sumo_import_commands_are_reproducible() -> None:
    config = load_villa_alemana_geo()
    get_command, build_command = sumo_import_commands(
        config, Path("C:/SUMO"), Path("data/villa-alemana-sumo")
    )
    assert "osmGet.py" in get_command[1]
    assert config.bbox_string in get_command
    assert "osmBuild.py" in build_command[1]
    assert config.vehicle_classes in build_command


def test_villa_alemana_simplified_scenario_is_core_compatible() -> None:
    scenario = load_scenario("configs/scenario-villa-alemana-v1.json")
    assert scenario.version == "villa-alemana-simplified-v1"
    assert len(scenario.stops) == 20
    assert len(scenario.lines) == 3
    for stop in (
        "M_LAS_AMERICAS",
        "M_LA_CONCEPCION",
        "M_VILLA_ALEMANA",
        "M_SARGENTO_ALDEA",
        "M_PENABLANCA",
    ):
        assert stop in scenario.stops
