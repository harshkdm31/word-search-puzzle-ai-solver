
"""Export word-search benchmark results to a CSV file."""

import csv
from pathlib import Path


CSV_FIELDS = [
    "algorithm",
    "grid_size",
    "word_list_size",
    "repeats",
    "words_found",
    "total_words",
    "missing_words",
    "all_words_found",
    "states_explored",
    "mean_time_ms",
    "median_time_ms",
    "min_time_ms",
    "max_time_ms",
    "experiment_grid_size",
    "requested_word_count",
]


def export_results_to_csv(results, output_path="benchmark_results.csv"):
    """
    Write benchmark results to CSV.

    Args:
        results: List of result dictionaries from run_benchmark().
        output_path: Destination CSV file path.

    Returns:
        Path to the created CSV file.
    """
    if not results:
        raise ValueError("Cannot export empty benchmark results.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()

        for result in results:
            row = result.copy()

            # Store missing words as one readable CSV cell.
            if isinstance(row.get("missing_words"), (list, tuple)):
                row["missing_words"] = "; ".join(row["missing_words"])

            writer.writerow(row)

    return path
