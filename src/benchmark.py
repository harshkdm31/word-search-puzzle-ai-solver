
"""Benchmark the three word-search solvers on identical puzzles."""

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

# Words of varying lengths for controlled experiments.
CANDIDATE_WORDS = [
    "CAT", "DOG", "SUN", "MAP", "KEY",
    "JAVA", "CODE", "TREE", "STAR", "MOON",
    "PYTHON", "SEARCH", "PUZZLE", "PLANET",
    "ALGORITHM", "STREAMLIT", "BACKTRACK",
]


def benchmark_puzzle(grid, words, repeats=5):
    """
    Benchmark every solver on the same grid and target-word list.

    Returns one result dictionary per solver.
    """
    if not grid or not grid[0]:
        raise ValueError("Grid must not be empty.")

    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Grid rows must all have the same length.")

    if not words:
        raise ValueError("Word list must not be empty.")

    if repeats < 1:
        raise ValueError("repeats must be at least 1.")

    # Take snapshots so solvers cannot accidentally change the inputs
    # used by later solvers.
    original_grid = [list(row) for row in grid]
    original_words = list(words)

    grid_size = f"{len(grid)}x{len(grid[0])}"
    results = []

    for solver_name, solver in SOLVERS.items():
        runtimes_ms = []
        final_result = None

        for _ in range(repeats):
            # Give every run an equivalent copy of the same puzzle.
            grid_copy = [row[:] for row in original_grid]
            words_copy = original_words[:]

            start = perf_counter()
            result = solver(grid_copy, words_copy)
            elapsed_ms = (perf_counter() - start) * 1000

            runtimes_ms.append(elapsed_ms)
            final_result = result

        found_words = final_result["found_words"]
        missing_words = final_result["missing_words"]

        results.append({
            "algorithm": solver_name,
            "grid_size": grid_size,
            "word_list_size": len(original_words),
            "repeats": repeats,
            "words_found": len(found_words),
            "total_words": len(original_words),
            "missing_words": list(missing_words),
            "all_words_found": len(missing_words) == 0,
            "states_explored": final_result["states_explored"],
            "mean_time_ms": mean(runtimes_ms),
            "median_time_ms": median(runtimes_ms),
            "min_time_ms": min(runtimes_ms),
            "max_time_ms": max(runtimes_ms),
        })

    return results


def run_benchmark(
    grid_sizes=(10, 15, 20),
    word_counts=(5, 10, 15),
    repeats=5,
):
    """
    Run multiple experiments at different grid and word-list sizes.

    Each experiment generates one puzzle, then benchmarks all three
    solvers against that exact puzzle.
    """
    if not grid_sizes or not word_counts:
        raise ValueError("Grid sizes and word counts must not be empty.")

    if any(size < 1 for size in grid_sizes):
        raise ValueError("Grid sizes must be positive.")

    if any(count < 1 for count in word_counts):
        raise ValueError("Word counts must be positive.")

    if repeats < 1:
        raise ValueError("repeats must be at least 1.")

    max_words = max(word_counts)
    usable_words = [
        word for word in CANDIDATE_WORDS
        if len(word) <= max(grid_sizes)
    ]

    if max_words > len(usable_words):
        raise ValueError(
            f"Requested up to {max_words} words, but only "
            f"{len(usable_words)} candidate words fit the largest grid."
        )

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

            # Generate exactly one puzzle for this experiment.
            selected_words = eligible_words[:count]
            puzzle = generate_puzzle(size, selected_words)

            # All three solvers receive this same puzzle.
            experiment_results = benchmark_puzzle(
                puzzle["grid"],
                puzzle["words"],
                repeats=repeats,
            )

            for result in experiment_results:
                result["experiment_grid_size"] = size
                result["requested_word_count"] = count

            all_results.extend(experiment_results)

    return all_results
