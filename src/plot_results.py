
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


# Drawn in this order. Marker sizes shrink and line styles differ so that
# solvers with identical values remain visible as concentric markers instead
# of one line silently hiding another. No data values are altered.
ALGORITHM_STYLES = {
    "DFS + Backtracking": {
        "color": "#F43F5E",
        "marker": "o",
        "linestyle": "-",
        "linewidth": 2.0,
        "markersize": 9,
        "zorder": 3,
    },
    "Trie Search": {
        "color": "#38BDF8",
        "marker": "s",
        "linestyle": "--",
        "linewidth": 1.8,
        "markersize": 6.5,
        "zorder": 4,
    },
    "Optimized Trie Search": {
        "color": "#10B981",
        "marker": "D",
        "linestyle": ":",
        "linewidth": 2.0,
        "markersize": 4.5,
        "zorder": 5,
    },
}
DEFAULT_STYLE = {
    "color": "#A855F7",
    "marker": "^",
    "linestyle": "-.",
    "linewidth": 1.6,
    "markersize": 5,
    "zorder": 2,
}

CHART_BG = "#111827"
AXES_BG = "#0B0F19"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
GRID = "#334155"


def _format_value(metric, value, _pos=None):
    """Tick formatter tailored to each metric."""
    if metric == "completion_percent":
        return f"{value:.0f}%"
    if metric == "states_explored":
        return f"{value:,.0f}"
    if abs(value) >= 100:
        return f"{value:,.0f}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _algorithm_order(algorithms):
    """Known solvers first (fixed draw order), then any others."""
    known = [name for name in ALGORITHM_STYLES if name in algorithms]
    others = sorted(name for name in algorithms if name not in ALGORITHM_STYLES)
    return known + others


def _save_metric_chart(data, metric, ylabel, title, output_path):
    """Plot one metric against grid size, with a line per algorithm."""
    from matplotlib.ticker import FuncFormatter, MaxNLocator

    grouped = (
        data.groupby(
            ["algorithm", "experiment_grid_size", "requested_word_count"],
            as_index=False,
        )[metric]
        .mean()
    )

    word_counts = sorted(grouped["requested_word_count"].unique())
    algorithms = _algorithm_order(grouped["algorithm"].unique())
    grid_sizes = sorted(grouped["experiment_grid_size"].unique())

    panels = len(word_counts)
    fig, axes = plt.subplots(
        1,
        panels,
        figsize=(max(5.2, 3.7 * panels), 2.9),
        squeeze=False,
        sharey=True,
        facecolor=CHART_BG,
    )

    is_percent = metric == "completion_percent"

    for ax, word_count in zip(axes[0], word_counts):
        ax.set_facecolor(AXES_BG)
        subset = grouped[grouped["requested_word_count"] == word_count]

        for algorithm in algorithms:
            line_data = subset[subset["algorithm"] == algorithm].sort_values(
                "experiment_grid_size"
            )

            if not line_data.empty:
                style = ALGORITHM_STYLES.get(algorithm, DEFAULT_STYLE)
                ax.plot(
                    line_data["experiment_grid_size"],
                    line_data[metric],
                    marker=style["marker"],
                    markersize=style["markersize"],
                    linestyle=style["linestyle"],
                    linewidth=style["linewidth"],
                    color=style["color"],
                    markeredgecolor=AXES_BG,
                    markeredgewidth=0.8,
                    zorder=style["zorder"],
                    clip_on=False,
                    label=algorithm,
                )

        # Honest note when every solver reports the same values here.
        pivot = subset.pivot_table(
            index="experiment_grid_size",
            columns="algorithm",
            values=metric,
        )
        if pivot.shape[1] > 1 and bool(
            (pivot.max(axis=1) - pivot.min(axis=1)).abs().max() < 1e-9
        ):
            ax.text(
                0.98, 0.04, "All solvers identical",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=7, color=MUTED, style="italic",
            )

        ax.set_title(
            f"{word_count} target words",
            color=TEXT, fontsize=9, fontweight="semibold", pad=6,
        )
        ax.set_xlabel("Grid size", color=MUTED, fontsize=8, labelpad=3)
        ax.set_xticks(grid_sizes)
        ax.set_xticklabels([f"{size}×{size}" for size in grid_sizes])
        if len(grid_sizes) == 1:
            ax.set_xlim(grid_sizes[0] - 1, grid_sizes[0] + 1)
        else:
            pad = (grid_sizes[-1] - grid_sizes[0]) * 0.06
            ax.set_xlim(grid_sizes[0] - pad, grid_sizes[-1] + pad)

        ax.tick_params(colors=MUTED, labelsize=7.5, length=3)
        for spine_name, spine in ax.spines.items():
            spine.set_visible(spine_name in ("left", "bottom"))
            spine.set_color(GRID)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.6,
                alpha=0.5, color=GRID)
        ax.yaxis.set_major_formatter(
            FuncFormatter(lambda v, p, m=metric: _format_value(m, v, p))
        )

    first_ax = axes[0][0]
    first_ax.set_ylabel(ylabel, color=MUTED, fontsize=8, labelpad=4)

    if is_percent:
        # Completion is a proportion; the axis never exceeds 100%.
        first_ax.set_ylim(0, 100)
        first_ax.set_yticks([0, 25, 50, 75, 100])
    else:
        top = grouped[metric].max()
        first_ax.set_ylim(0, top * 1.12 if top and top > 0 else 1)
        first_ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    handles, labels = first_ax.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper right",
        bbox_to_anchor=(1.0, 1.0),
        ncol=max(1, len(labels)),
        fontsize=7.5,
        frameon=False,
        labelcolor=TEXT,
        handlelength=2.4,
        columnspacing=1.2,
    )
    fig.text(
        0.0, 0.985, title,
        ha="left", va="top",
        color=TEXT, fontsize=10.5, fontweight="bold",
    )

    fig.tight_layout(rect=[0, 0, 1, 0.88], w_pad=1.2)
    fig.savefig(
        output_path,
        dpi=170,
        bbox_inches="tight",
        pad_inches=0.12,
        facecolor=fig.get_facecolor(),
        edgecolor="none",
    )
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
