
import pytest

from src.trie_solver import solve_trie
from src.trie_solver import solve_trie_optimized

def test_finds_horizontal_words():
    grid = [
        list("CATX"),
        list("DOGX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT", "DOG"])

    assert set(result["found_words"]) == {"CAT", "DOG"}


def test_finds_diagonal_word():
    grid = [
        list("CXXX"),
        list("XAXX"),
        list("XXTX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT"])

    assert "CAT" in result["found_words"]
    assert result["placements"]["CAT"] == [
        (0, 0), (1, 1), (2, 2)
    ]


def test_finds_word_in_reverse_direction():
    grid = [
        list("TACX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT"])

    assert "CAT" in result["found_words"]
    assert result["placements"]["CAT"] == [
        (0, 2), (0, 1), (0, 0)
    ]


def test_reports_missing_words():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT", "DOG"])

    assert "CAT" in result["found_words"]
    assert "DOG" in result["missing_words"]


def test_shared_prefix_words():
    grid = [
        list("CARD"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAR", "CARD", "CAT"])

    assert "CAR" in result["found_words"]
    assert "CARD" in result["found_words"]
    assert "CAT" in result["missing_words"]


def test_records_search_events():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT"])
    event_types = {event["type"] for event in result["events"]}

    assert "explore" in event_types
    assert "match" in event_types
    assert "word_found" in event_types
    assert result["states_explored"] > 0


def test_duplicate_targets_are_removed():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie(grid, ["CAT", "CAT"])

    assert result["found_words"] == ["CAT"]
    assert len(result["placements"]) == 1


def test_rejects_non_rectangular_grid():
    grid = [list("CAT"), list("XX")]

    with pytest.raises(ValueError):
        solve_trie(grid, ["CAT"])


def test_rejects_invalid_target():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    with pytest.raises(ValueError):
        solve_trie(grid, ["CAT!"])

def test_optimized_solver_finds_all_words():
    grid = [
        list("CARD"),
        list("DOGX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie_optimized(
        grid, ["CAR", "CARD", "DOG"]
    )

    assert set(result["found_words"]) == {"CAR", "CARD", "DOG"}
    assert result["missing_words"] == []


def test_optimized_solver_reports_missing_words():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie_optimized(grid, ["CAT", "DOG"])

    assert result["found_words"] == ["CAT"]
    assert result["missing_words"] == ["DOG"]


def test_optimized_solver_preserves_coordinates():
    grid = [
        list("CXXX"),
        list("XAXX"),
        list("XXTX"),
        list("XXXX"),
    ]

    result = solve_trie_optimized(grid, ["CAT"])

    assert result["placements"]["CAT"] == [
        (0, 0), (1, 1), (2, 2)
    ]


def test_optimized_solver_handles_shared_prefixes():
    grid = [
        list("CART"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie_optimized(
        grid, ["CAR", "CART", "CAT"]
    )

    assert "CAR" in result["found_words"]
    assert "CART" in result["found_words"]
    assert "CAT" in result["missing_words"]


def test_optimized_solver_records_events():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_trie_optimized(grid, ["CAT"])
    event_types = {event["type"] for event in result["events"]}

    assert "explore" in event_types
    assert "word_found" in event_types
    assert result["states_explored"] > 0


def test_optimized_solver_rejects_invalid_grid():
    grid = [list("CAT"), list("XX")]

    with pytest.raises(ValueError):
        solve_trie_optimized(grid, ["CAT"])
