
import pandas as pd
import pytest

from src.plot_results import (
    generate_comparison_charts,
    load_benchmark_results,
)


def sample_results():
    rows = []

    for algorithm, runtime, states in [
        ("DFS + Backtracking", 2.0, 100),
        ("Trie Search", 1.5, 70),
        ("Optimized Trie Search", 1.0, 40),
    ]:
        rows.append({
            "algorithm": algorithm,
            "mean_time_ms": runtime,
            "states_explored": states,
            "words_found": 2,
            "total_words": 2,
            "experiment_grid_size": 10,
            "requested_word_count": 2,
        })

    return pd.DataFrame(rows)


def test_load_benchmark_results(tmp_path):
    csv_path = tmp_path / "benchmark_results.csv"
    sample_results().to_csv(csv_path, index=False)

    data = load_benchmark_results(csv_path)

    assert len(data) == 3
    assert "algorithm" in data.columns
    assert "mean_time_ms" in data.columns


def test_load_results_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_benchmark_results(tmp_path / "missing.csv")


def test_load_results_rejects_missing_columns(tmp_path):
    csv_path = tmp_path / "incomplete.csv"
    pd.DataFrame({"algorithm": ["DFS"]}).to_csv(
        csv_path, index=False
    )

    with pytest.raises(ValueError, match="missing required columns"):
        load_benchmark_results(csv_path)


def test_generate_comparison_charts(tmp_path):
    csv_path = tmp_path / "benchmark_results.csv"
    output_dir = tmp_path / "charts"

    sample_results().to_csv(csv_path, index=False)

    chart_paths = generate_comparison_charts(
        csv_path=csv_path,
        output_dir=output_dir,
    )

    assert len(chart_paths) == 3

    for chart_path in chart_paths:
        assert chart_path.exists()
        assert chart_path.stat().st_size > 0
