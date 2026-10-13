
from src.evaluation import evaluate_solvers, get_evaluation_summary


def test_evaluate_solvers_returns_all_three_algorithms():
    grid = [
        list("CAT"),
        list("DOG"),
        list("RAT"),
    ]
    words = ["CAT", "DOG", "RAT", "BIRD"]

    results = evaluate_solvers(grid, words)

    assert len(results) == 3
    assert "DFS + Backtracking" in results
    assert "Trie Search" in results
    assert "Optimized Trie Search" in results


def test_all_solvers_find_the_same_words():
    grid = [
        list("CAT"),
        list("DOG"),
        list("RAT"),
    ]
    words = ["CAT", "DOG", "RAT", "BIRD"]

    results = evaluate_solvers(grid, words)

    expected = {"CAT", "DOG", "RAT"}

    for metrics in results.values():
        assert set(metrics["found_words"]) == expected
        assert set(metrics["missing_words"]) == {"BIRD"}


def test_metrics_contain_required_fields():
    grid = [list("CAT"), list("DOG"), list("RAT")]
    words = ["CAT", "DOG"]

    results = evaluate_solvers(grid, words)

    required_fields = {
        "algorithm",
        "grid_size",
        "word_list_size",
        "words_found",
        "total_words",
        "states_explored",
        "execution_time_ms",
        "found_words",
        "missing_words",
        "placements",
    }

    for metrics in results.values():
        assert required_fields.issubset(metrics.keys())
        assert metrics["execution_time_ms"] >= 0
        assert metrics["states_explored"] >= 0


def test_evaluation_summary_has_one_row_per_solver():
    grid = [list("CAT"), list("DOG"), list("RAT")]
    words = ["CAT", "DOG"]

    results = evaluate_solvers(grid, words)
    summary = get_evaluation_summary(results)

    assert len(summary) == 3
    assert summary[0]["Algorithm"] == "DFS + Backtracking"
    assert "Execution Time (ms)" in summary[0]


def test_evaluation_handles_empty_word_list():
    grid = [list("CAT"), list("DOG"), list("RAT")]

    results = evaluate_solvers(grid, [])

    for metrics in results.values():
        assert metrics["words_found"] == 0
        assert metrics["total_words"] == 0
