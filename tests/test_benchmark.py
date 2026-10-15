
import pytest

import src.benchmark as benchmark


def fake_solver(grid, words):
    """A predictable solver result for testing the benchmark."""
    return {
        "found_words": words[:],
        "missing_words": [],
        "states_explored": 10,
        "placements": {},
        "execution_time": 0.001,
    }


def test_benchmark_runs_all_three_solvers(monkeypatch):
    monkeypatch.setattr(
        benchmark,
        "SOLVERS",
        {
            "DFS + Backtracking": fake_solver,
            "Trie Search": fake_solver,
            "Optimized Trie Search": fake_solver,
        },
    )

    grid = [["C", "A"], ["T", "D"]]
    words = ["CAT"]

    results = benchmark.benchmark_puzzle(
        grid, words, repeats=2
    )

    assert len(results) == 3
    assert {result["algorithm"] for result in results} == {
        "DFS + Backtracking",
        "Trie Search",
        "Optimized Trie Search",
    }


def test_benchmark_records_expected_metrics(monkeypatch):
    monkeypatch.setattr(
        benchmark,
        "SOLVERS",
        {"Test Solver": fake_solver},
    )

    results = benchmark.benchmark_puzzle(
        [["C", "A"], ["T", "D"]],
        ["CAT"],
        repeats=2,
    )

    result = results[0]

    assert result["grid_size"] == "2x2"
    assert result["word_list_size"] == 1
    assert result["repeats"] == 2
    assert result["words_found"] == 1
    assert result["total_words"] == 1
    assert result["missing_words"] == []
    assert result["all_words_found"] is True
    assert result["states_explored"] == 10
    assert result["mean_time_ms"] >= 0
    assert result["median_time_ms"] >= 0
    assert result["min_time_ms"] >= 0
    assert result["max_time_ms"] >= result["min_time_ms"]


@pytest.mark.parametrize(
    ("grid", "words", "repeats"),
    [
        ([], ["CAT"], 1),
        ([["C", "A"], ["T"]], ["CAT"], 1),
        ([["C"]], [], 1),
        ([["C"]], ["C"], 0),
    ],
)
def test_benchmark_rejects_invalid_inputs(grid, words, repeats):
    with pytest.raises(ValueError):
        benchmark.benchmark_puzzle(grid, words, repeats)


def test_all_solvers_receive_the_same_puzzle(monkeypatch):
    received = []

    def recording_solver(grid, words):
        received.append((grid, words))
        return fake_solver(grid, words)

    monkeypatch.setattr(
        benchmark,
        "SOLVERS",
        {
            "Solver A": recording_solver,
            "Solver B": recording_solver,
            "Solver C": recording_solver,
        },
    )

    original_grid = [["C", "A"], ["T", "D"]]
    original_words = ["CAT"]

    benchmark.benchmark_puzzle(
        original_grid, original_words, repeats=1
    )

    assert len(received) == 3

    for grid, words in received:
        assert grid == original_grid
        assert words == original_words

    # Each solver receives its own copy, not a shared mutable object.
    assert len({id(grid) for grid, _ in received}) == 3


def test_run_benchmark_generates_one_puzzle_per_experiment(
    monkeypatch,
):
    generation_calls = []

    def fake_generate_puzzle(size, words):
        generation_calls.append((size, list(words)))
        return {
            "grid": [["C", "A"], ["T", "D"]],
            "words": list(words),
        }

    monkeypatch.setattr(
        benchmark,
        "generate_puzzle",
        fake_generate_puzzle,
    )
    monkeypatch.setattr(
        benchmark,
        "SOLVERS",
        {
            "Solver A": fake_solver,
            "Solver B": fake_solver,
            "Solver C": fake_solver,
        },
    )

    results = benchmark.run_benchmark(
        grid_sizes=(10,),
        word_counts=(2,),
        repeats=1,
    )

    assert len(generation_calls) == 1
    assert len(results) == 3
    assert {
        result["algorithm"] for result in results
    } == {"Solver A", "Solver B", "Solver C"}


def test_run_benchmark_rejects_invalid_settings():
    with pytest.raises(ValueError):
        benchmark.run_benchmark(grid_sizes=(), word_counts=(2,))

    with pytest.raises(ValueError):
        benchmark.run_benchmark(grid_sizes=(0,), word_counts=(2,))

    with pytest.raises(ValueError):
        benchmark.run_benchmark(grid_sizes=(10,), word_counts=(0,))

