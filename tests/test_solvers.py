
import pytest

from src.dfs_solver import solve_dfs


def test_finds_horizontal_word():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["CAT"])

    assert "CAT" in result["found_words"]
    assert result["placements"]["CAT"] == [(0, 0), (0, 1), (0, 2)]


def test_finds_diagonal_word():
    grid = [
        list("CXXX"),
        list("XAXX"),
        list("XXTX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["CAT"])

    assert "CAT" in result["found_words"]
    assert result["placements"]["CAT"] == [(0, 0), (1, 1), (2, 2)]


def test_finds_reversed_direction():
    grid = [
        list("TACX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["CAT"])

    assert "CAT" in result["found_words"]
    assert result["placements"]["CAT"] == [(0, 2), (0, 1), (0, 0)]


def test_reports_missing_word():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["DOG"])

    assert result["found_words"] == []
    assert result["missing_words"] == ["DOG"]


def test_duplicate_targets_are_removed():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["CAT", "CAT"])

    assert result["found_words"] == ["CAT"]
    assert len(result["placements"]) == 1


def test_records_search_events():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    result = solve_dfs(grid, ["CAT"])
    event_types = {event["type"] for event in result["events"]}

    assert "explore" in event_types
    assert "match" in event_types
    assert "word_found" in event_types
    assert result["states_explored"] > 0


def test_rejects_non_rectangular_grid():
    grid = [
        list("CAT"),
        list("XX"),
    ]

    with pytest.raises(ValueError):
        solve_dfs(grid, ["CAT"])


def test_rejects_invalid_target():
    grid = [
        list("CATX"),
        list("XXXX"),
        list("XXXX"),
        list("XXXX"),
    ]

    with pytest.raises(ValueError):
        solve_dfs(grid, ["CAT!"])
