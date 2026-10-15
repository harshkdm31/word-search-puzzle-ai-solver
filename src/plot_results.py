
"""Generate comparison charts from exported benchmark results."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_CSV = Path("benchmark_results.csv")
DEFAULT_OUTPUT_DIR = Path("reports") / "benchmark_charts"


def load_benchmark_results(csv_path=DEFAULT_CSV):
    """Load and validate benchmark results from CSV."""
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Benchmark CSV not found: {csv_path}. "
            "Run the benchmark and CSV export first."
        )

    data = pd.read_csv(csv_path)

    required_columns = {
        "algorithm",
        "mean_time_ms",
        "states_explored",
        "words_found",
        "total_words",
        "experiment_grid_size",
        "requested_word_count",
    }

    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(sorted(missing))}"
        )

    if data.empty:
        raise ValueError("Benchmark CSV contains no results.")

    return data


def _save_metric_chart(data, metric, ylabel, title, output_path):
    """Plot one metric against grid size, with a line per algorithm."""
    grouped = (
        data.groupby(
            ["algorithm", "experiment_grid_size", "requested_word_count"],
            as_index=False,
        )[metric]
        .mean()
    )

    word_counts = sorted(grouped["requested_word_count"].unique())
    algorithms = sorted(grouped["algorithm"].unique())

    fig, axes = plt.subplots(
        1,
        len(word_counts),
        figsize=(6 * len(word_counts), 4.5),
        squeeze=False,
    )

    for ax, word_count in zip(axes[0], word_counts):
        subset = grouped[grouped["requested_word_count"] == word_count]

        for algorithm in algorithms:
            line_data = subset[subset["algorithm"] == algorithm].sort_values(
                "experiment_grid_size"
            )

            if not line_data.empty:
                ax.plot(
                    line_data["experiment_grid_size"],
                    line_data[metric],
                    marker="o",
                    label=algorithm,
                )

        ax.set_title(f"{word_count} target words")
        ax.set_xlabel("Grid size (N × N)")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize="small")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_comparison_charts(
    csv_path=DEFAULT_CSV,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    """Create and save runtime, search-state, and word-completion charts."""
    data = load_benchmark_results(csv_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_specs = [
        (
            "mean_time_ms",
            "Mean execution time (ms)",
            "Solver Runtime Comparison",
            "runtime_comparison.png",
        ),
        (
            "states_explored",
            "States explored",
            "Search Effort Comparison",
            "states_explored_comparison.png",
        ),
    ]

    for metric, ylabel, title, filename in chart_specs:
        _save_metric_chart(
            data,
            metric,
            ylabel,
            title,
            output_dir / filename,
        )

    # Compare the proportion of target words found.
    data = data.copy()
    data["completion_percent"] = (
        data["words_found"] / data["total_words"].replace(0, pd.NA)
    ) * 100

    _save_metric_chart(
        data,
        "completion_percent",
        "Target words found (%)",
        "Word-Finding Success Comparison",
        output_dir / "word_completion_comparison.png",
    )

    return [
        output_dir / "runtime_comparison.png",
        output_dir / "states_explored_comparison.png",
        output_dir / "word_completion_comparison.png",
    ]


if __name__ == "__main__":
    chart_paths = generate_comparison_charts()

    print("Comparison charts generated:")
    for chart_path in chart_paths:
        print(f"- {chart_path}")
