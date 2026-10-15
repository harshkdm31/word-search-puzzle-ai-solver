
import csv

import pytest

from src.export_results import export_results_to_csv


def test_export_results_creates_csv_with_headers(tmp_path):
    results = [
        {
            "algorithm": "DFS + Backtracking",
            "grid_size": "10x10",
            "word_list_size": 2,
            "repeats": 3,
            "words_found": 2,
            "total_words": 2,
            "missing_words": [],
            "all_words_found": True,
            "states_explored": 25,
            "mean_time_ms": 1.2,
            "median_time_ms": 1.1,
            "min_time_ms": 1.0,
            "max_time_ms": 1.5,
            "experiment_grid_size": 10,
            "requested_word_count": 2,
        }
    ]

    output_file = tmp_path / "results.csv"
    created_path = export_results_to_csv(results, output_file)

    assert created_path.exists()

    with created_path.open(
        "r", newline="", encoding="utf-8"
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["algorithm"] == "DFS + Backtracking"
    assert rows[0]["words_found"] == "2"
    assert rows[0]["all_words_found"] == "True"


def test_export_results_formats_missing_words(tmp_path):
    results = [
        {
            "algorithm": "Trie Search",
            "missing_words": ["PYTHON", "SEARCH"],
        }
    ]

    output_file = tmp_path / "results.csv"
    export_results_to_csv(results, output_file)

    with output_file.open(
        "r", newline="", encoding="utf-8"
    ) as csv_file:
        row = next(csv.DictReader(csv_file))

    assert row["missing_words"] == "PYTHON; SEARCH"


def test_export_results_rejects_empty_results(tmp_path):
    with pytest.raises(ValueError):
        export_results_to_csv([], tmp_path / "results.csv")

