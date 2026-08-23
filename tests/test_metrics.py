from buscomodin.metrics import percentile, summarize_metrics


def test_percentile_interpolates() -> None:
    assert percentile([0, 10, 20, 30], 0.5) == 15.0


def test_metrics_cover_m0_outputs() -> None:
    metrics = summarize_metrics(
        wait_times=[1, 2, 3, 10],
        left_behind_count=2,
        load_factors=[0.25, 0.75],
        observed_headways=[10, 12, 14],
        generated_passengers=5,
        boarded_passengers=4,
    )
    assert metrics["mean_wait_minutes"] == 4.0
    assert metrics["passengers_left_behind"] == 2
    assert metrics["mean_load_factor"] == 0.5
    assert metrics["mean_observed_headway_minutes"] == 12.0
