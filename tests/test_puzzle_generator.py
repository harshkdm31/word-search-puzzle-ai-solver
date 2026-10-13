
import pytest

from src.puzzle_generator import generate_puzzle


def test_generates_correct_grid_size():
    result = generate_puzzle(10, ["PYTHON", "SEARCH"], seed=42)

    assert len(result["grid"]) == 10
    assert all(len(row) == 10 for row in result["grid"])


def test_all_words_are_placed_correctly():
    result = generate_puzzle(
        10, ["PYTHON", "SEARCH", "DATA"], seed=42
    )

    grid = result["grid"]

    for word, coordinates in result["placements"].items():
        extracted = "".join(
            grid[row][col] for row, col in coordinates
        )
        assert extracted == word


def test_grid_contains_only_uppercase_letters():
    result = generate_puzzle(10, ["PYTHON"], seed=42)

    assert all(
        cell in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for row in result["grid"]
        for cell in row
    )


def test_duplicate_words_are_removed():
    result = generate_puzzle(
        10, ["Python", "PYTHON", "Data"], seed=42
    )

    assert result["words"] == ["PYTHON", "DATA"]
    assert len(result["placements"]) == 2


def test_rejects_invalid_grid_size():
    with pytest.raises(ValueError):
        generate_puzzle(4, ["CAT"])


def test_rejects_word_longer_than_grid():
    with pytest.raises(ValueError):
        generate_puzzle(5, ["ELEPHANT"])


def test_rejects_empty_word_list():
    with pytest.raises(ValueError):
        generate_puzzle(10, [])


def test_seed_produces_repeatable_puzzle():
    first = generate_puzzle(10, ["PYTHON", "DATA"], seed=42)
    second = generate_puzzle(10, ["PYTHON", "DATA"], seed=42)

    assert first == second
