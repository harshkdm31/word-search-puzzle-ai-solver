
"""Benchmark three word-search solvers on identical puzzles."""

from statistics import mean, median
from time import perf_counter

from src.puzzle_generator import generate_puzzle
from src.dfs_solver import solve_dfs
from src.trie_solver import solve_trie, solve_trie_optimized


SOLVERS = {
    "DFS + Backtracking": solve_dfs,
    "Trie Search": solve_trie,
    "Optimized Trie Search": solve_trie_optimized,
}

CANDIDATE_WORDS = [
    "CAT", "DOG", "SUN", "MAP", "KEY",
    "JAVA", "CODE", "TREE", "STAR", "MOON",
    "PYTHON", "SEARCH", "PUZZLE", "PLANET",
    "ALGORITHM", "STREAMLIT", "BACKTRACK",
]


def _copy_grid(grid):
    """Return an independent copy of a grid."""
    return [list(row) for row in grid]


def _validate_result(grid, result, expected_words):
    """Check reported words and ensure every placement is valid."""
    if not isinstance(result, dict):
        raise ValueError("A solver returned an invalid result.")

    required = {"found_words", "missing_words", "placements",
                "states_explored"}
    if not required.issubset(result):
        raise ValueError("A solver result is missing required fields.")

    found = set(result["found_words"])
    missing = set(result["missing_words"])
    placements = result["placements"]

    if found & missing or found | missing != expected_words:
        raise ValueError("A solver returned inconsistent word results.")
        
    if set(placements) != found:
        raise ValueError("Found words and placements do not match.")

    rows = len(grid)
    cols = len(grid[0])
    normalized_grid = [
        [str(cell).upper() for cell in row] for row in grid
    ]

    for word, path in placements.items():
        if len(path) != len(word) or not path:
            raise ValueError(f"Invalid placement length for {word!r}.")

        for row, col in path:
            if not (0 <= row < rows and 0 <= col < cols):
                raise ValueError(f"Placement for {word!r} is out of bounds.")

        letters = "".join(
            normalized_grid[row][col] for row, col in path
        )
        if letters != word:
            raise ValueError(
                f"Placement for {word!r} spells {letters!r}, not the word."
            )

        if len(path) > 1:
            dr = path[1][0] - path[0][0]
            dc = path[1][1] - path[0][1]

            if (dr, dc) == (0, 0) or abs(dr) > 1 or abs(dc) > 1:
                raise ValueError(f"Invalid direction for {word!r}.")

            for previous, current in zip(path, path[1:]):
                if (
                    current[0] - previous[0] != dr
                    or current[1] - previous[1] != dc
                ):
                    raise ValueError(
                        f"Placement for {word!r} is not a straight line."
                    )


def benchmark_puzzle(grid, words, repeats=30, warmups=2):
    """
    Benchmark every solver on the same puzzle.

    Warm-ups are excluded from timing summaries. Runtime includes
    the solver's own setup and search-event generation.
    """
    if not grid or not grid[0]:
        raise ValueError("Grid must not be empty.")

    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Grid rows must all have the same length.")

    if not words:
        raise ValueError("Word list must not be empty.")

    if repeats < 1:
        raise ValueError("repeats must be at least 1.")

    if warmups < 0:
        raise ValueError("warmups cannot be negative.")

    original_grid = _copy_grid(grid)
    original_words = list(words)

    expected_words = {
        "".join(word.split()).upper() for word in original_words
    }
    if any(
        not word or not word.isascii() or not word.isalpha()
        for word in expected_words
    ):
        raise ValueError("All target words must contain ASCII letters only.")

    grid_size = f"{len(grid)}x{len(grid[0])}"
    results = []
    found_sets = {}

    for solver_name, solver in SOLVERS.items():
        # Warm-up runs are not included in measured runtimes.
        for _ in range(warmups):
            solver(_copy_grid(original_grid), original_words[:])

        runtimes_ms = []
        final_result = None

        for _ in range(repeats):
            grid_copy = _copy_grid(original_grid)
            words_copy = original_words[:]

            start = perf_counter()
            result = solver(grid_copy, words_copy)
            elapsed_ms = (perf_counter() - start) * 1000

            _validate_result(original_grid, result, expected_words)

            runtimes_ms.append(elapsed_ms)
            final_result = result

        found = set(final_result["found_words"])
        found_sets[solver_name] = found

        missing_words = list(final_result["missing_words"])

        results.append({
            "algorithm": solver_name,
            "grid_size": grid_size,
            "word_list_size": len(expected_words),
            "repeats": repeats,
            "warmups": warmups,
            "words_found": len(found),
            "total_words": len(expected_words),
            "missing_words": missing_words,
            "all_words_found": len(missing_words) == 0,
            "states_explored": final_result["states_explored"],
            "mean_time_ms": mean(runtimes_ms),
            "median_time_ms": median(runtimes_ms),
            "min_time_ms": min(runtimes_ms),
            "max_time_ms": max(runtimes_ms),
        })

    # All solvers must agree on which words are present in the grid.
    reference_name = next(iter(found_sets))
    reference_found = found_sets[reference_name]

    for solver_name, found in found_sets.items():
        if found != reference_found:
            raise ValueError(
                f"Correctness mismatch: {solver_name} found "
                f"{sorted(found)}, but {reference_name} found "
                f"{sorted(reference_found)}."
            )

    return results


def run_benchmark(
    grid_sizes=(10, 15, 20),
    word_counts=(5, 10, 15),
    repeats=30,
    warmups=2,
):
    """Run experiments on generated puzzles shared by all solvers."""
    if not grid_sizes or not word_counts:
        raise ValueError("Grid sizes and word counts must not be empty.")

    if any(size < 1 for size in grid_sizes):
        raise ValueError("Grid sizes must be positive.")

    if any(count < 1 for count in word_counts):
        raise ValueError("Word counts must be positive.")

    if repeats < 1:
        raise ValueError("repeats must be at least 1.")

    if warmups < 0:
        raise ValueError("warmups cannot be negative.")

    usable_words = [
        word for word in CANDIDATE_WORDS
        if len(word) <= max(grid_sizes)
    ]

    all_results = []

    for size in grid_sizes:
        eligible_words = [
            word for word in usable_words if len(word) <= size
        ]

        for count in word_counts:
            if count > len(eligible_words):
                raise ValueError(
                    f"Cannot select {count} candidate words for a "
                    f"{size}x{size} grid. Reduce the word count or "
                    "add more suitable candidate words."
                )

            selected_words = eligible_words[:count]
            puzzle = generate_puzzle(size, selected_words)

            experiment_results = benchmark_puzzle(
                puzzle["grid"],
                puzzle["words"],
                repeats=repeats,
                warmups=warmups,
            )

            for result in experiment_results:
                result["experiment_grid_size"] = size
                result["requested_word_count"] = count

            all_results.extend(experiment_results)

    return all_results
