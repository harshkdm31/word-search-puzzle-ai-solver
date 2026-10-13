
"""Evaluate and compare the three word-search solving algorithms."""

from time import perf_counter

from src.dfs_solver import solve_dfs
from src.trie_solver import solve_trie, solve_trie_optimized


def evaluate_solvers(grid, words):
    """Run all three solvers on the same puzzle and compare their results.

    Args:
        grid: A 2D list representing the puzzle grid.
        words: A list of target words to search for.

    Returns:
        A dictionary containing each solver's metrics.
    """
    solvers = {
        "DFS + Backtracking": solve_dfs,
        "Trie Search": solve_trie,
        "Optimized Trie Search": solve_trie_optimized,
    }

    results = {}

    grid_size = f"{len(grid)}x{len(grid[0])}" if grid else "0x0"
    word_list_size = len(words)

    for solver_name, solver_function in solvers.items():
        start_time = perf_counter()
        solver_result = solver_function(grid, words)
        elapsed_ms = (perf_counter() - start_time) * 1000

        results[solver_name] = {
            "algorithm": solver_name,
            "grid_size": grid_size,
            "word_list_size": word_list_size,
            "words_found": len(solver_result["found_words"]),
            "total_words": word_list_size,
            "states_explored": solver_result["states_explored"],
            "execution_time_ms": round(elapsed_ms, 4),
            "found_words": solver_result["found_words"],
            "missing_words": solver_result["missing_words"],
            "placements": solver_result["placements"],
        }

    return results


def get_evaluation_summary(results):
    """Create a compact, display-friendly summary of evaluation results."""
    summary = []

    for solver_name, metrics in results.items():
        summary.append({
            "Algorithm": solver_name,
            "Grid Size": metrics["grid_size"],
            "Words in List": metrics["word_list_size"],
            "Words Found": metrics["words_found"],
            "States Explored": metrics["states_explored"],
            "Execution Time (ms)": metrics["execution_time_ms"],
        })

    return summary
