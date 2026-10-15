
import time
import html
import re

import pandas as pd
import streamlit as st

from src.puzzle_generator import generate_puzzle
from src.dfs_solver import solve_dfs
from src.trie_solver import solve_trie, solve_trie_optimized
from src.evaluation import evaluate_solvers, get_evaluation_summary
from src.animation import TracePlayer
from streamlit_autorefresh import st_autorefresh
from components.interactive_grid import interactive_grid
from src.benchmark import run_benchmark
from src.export_results import export_results_to_csv
from src.plot_results import generate_comparison_charts
from pathlib import Path

st.set_page_config(
    page_title="Word Search Puzzle AI Solver",
    page_icon="🔎",
    layout="wide",
)

# Custom Theme CSS & Typography
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    :root {
        --bg: #0B0F19;
        --surface: #111827;
        --surface-2: #151D2F;
        --border: rgba(148, 163, 184, 0.16);
        --border-strong: rgba(148, 163, 184, 0.28);
        --accent: #6366F1;
        --accent-soft: rgba(99, 102, 241, 0.14);
        --text: #F8FAFC;
        --text-2: #CBD5E1;
        --muted: #94A3B8;
        --found: #10B981;
        --radius: 10px;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .stApp {
        background-color: var(--bg);
        background-image:
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.07) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.05) 0px, transparent 45%);
    }

    /* ---------- Compact page rhythm ---------- */
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px;
    }

    [data-testid="stVerticalBlock"] { gap: 0.75rem; }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 9999px;
        background: var(--accent-soft);
        border: 1px solid rgba(129, 140, 248, 0.3);
        color: #A5B4FC;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        font-size: clamp(1.7rem, 2.6vw, 2.3rem) !important;
        padding: 0.1rem 0 0 0 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E7FF 60%, #A5B4FC 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    h2 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        font-size: 1.4rem !important;
        color: var(--text) !important;
        padding: 0.2rem 0 0 0 !important;
    }

    h3 {
        font-weight: 650 !important;
        letter-spacing: -0.01em !important;
        font-size: 1.08rem !important;
        color: #E2E8F0 !important;
        padding: 0.35rem 0 0.1rem 0 !important;
    }

    .section-lead {
        color: var(--muted);
        font-size: 0.92rem;
        margin: -0.35rem 0 0.25rem 0;
    }

    .inline-label {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin: 0.2rem 0 0.35rem 0;
    }

    [data-testid="stCaptionContainer"], .stCaption {
        color: var(--muted) !important;
    }

    /* ---------- Dividers ---------- */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.35), transparent) !important;
        margin: 1.1rem 0 !important;
    }

    /* ---------- Metric cards ---------- */
    [data-testid="stMetric"] {
        background: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 12px 16px !important;
    }

    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    /* ---------- Buttons (old + new Streamlit test ids) ---------- */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        min-height: 2.4rem;
        transition: background 0.15s ease, border-color 0.15s ease,
                    box-shadow 0.15s ease, filter 0.15s ease !important;
    }

    [data-testid="baseButton-primary"],
    [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        border: 1px solid rgba(196, 181, 253, 0.35) !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 10px rgba(79, 70, 229, 0.35) !important;
    }

    [data-testid="baseButton-primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        filter: brightness(1.1) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45) !important;
    }

    [data-testid="baseButton-secondary"],
    [data-testid="stBaseButton-secondary"] {
        background: #172033 !important;
        border: 1px solid var(--border-strong) !important;
        color: #E2E8F0 !important;
    }

    [data-testid="baseButton-secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover {
        background: #1E293B !important;
        border-color: var(--accent) !important;
        color: #FFFFFF !important;
    }

    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible,
    [data-baseweb="tab"]:focus-visible {
        outline: 2px solid #A5B4FC !important;
        outline-offset: 2px !important;
        box-shadow: none !important;
    }

    .stButton > button:disabled,
    .stDownloadButton > button:disabled {
        opacity: 0.45 !important;
        filter: grayscale(0.4) !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
    }

    /* ---------- Expanders, tabs, tables ---------- */
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] {
        background: rgba(17, 24, 39, 0.7) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }

    [data-testid="stExpander"] summary {
        font-weight: 600;
    }

    [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid var(--border);
    }

    [data-baseweb="tab"] {
        padding: 6px 12px !important;
        font-weight: 600 !important;
        color: var(--muted) !important;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--text) !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }

    [data-testid="stImage"] img {
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1322 0%, #080C14 100%) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* ---------- Progress ---------- */
    [data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%) !important;
        border-radius: 9999px !important;
    }

    .progress-card {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 10px 14px;
        font-size: 0.88rem;
        color: var(--text-2);
    }

    .progress-head {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 6px;
    }

    .progress-head strong {
        color: var(--text);
        font-family: 'JetBrains Mono', ui-monospace, monospace;
    }

    .muted { color: var(--muted); font-size: 0.8rem; }

    .progress-track {
        height: 6px;
        border-radius: 9999px;
        background: rgba(148, 163, 184, 0.15);
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #059669, #10B981);
        border-radius: 9999px;
    }

    .progress-remaining {
        margin-top: 8px;
        font-size: 0.84rem;
        line-height: 1.45;
        word-break: break-word;
    }

    .progress-remaining strong { color: var(--text); }

    /* ---------- Legend ---------- */
    .legend-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin: 2px 0 4px 0;
    }

    .legend-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 2px 9px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
    }

    .legend-dot { width: 8px; height: 8px; border-radius: 2px; }

    .pill-explored { background: rgba(59, 130, 246, 0.14); color: #93C5FD; border: 1px solid rgba(59, 130, 246, 0.35); }
    .dot-explored { background: #3B82F6; }
    .pill-backtracked { background: rgba(239, 68, 68, 0.14); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.35); }
    .dot-backtracked { background: #EF4444; }
    .pill-matched { background: rgba(245, 158, 11, 0.14); color: #FDE68A; border: 1px solid rgba(245, 158, 11, 0.35); }
    .dot-matched { background: #F59E0B; }
    .pill-active { background: rgba(139, 92, 246, 0.16); color: #DDD6FE; border: 1px solid rgba(139, 92, 246, 0.45); }
    .dot-active { background: #8B5CF6; }
    .pill-found { background: rgba(16, 185, 129, 0.16); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.45); }
    .dot-found { background: #10B981; }

    /* ---------- Word badges ---------- */
    .target-words-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 2px 0 6px 0;
    }

    .target-word-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 7px;
        font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    .target-word-badge.pending {
        background: var(--surface-2);
        border: 1px solid var(--border-strong);
        color: var(--text-2);
    }

    .target-word-badge.found {
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.55);
        color: #6EE7B7;
    }

    /* ---------- Playback status ---------- */
    .event-card {
        padding: 10px 14px;
        border-radius: var(--radius);
        background: var(--surface-2);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-left: 3px solid var(--accent);
        color: var(--text);
        font-size: 0.92rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    .event-card strong { color: #C7D2FE; font-weight: 700; }
    .event-card code {
        background: rgba(148, 163, 184, 0.12);
        padding: 1px 5px;
        border-radius: 4px;
        font-size: 0.85em;
    }

    .stat-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
        margin-bottom: 8px;
    }

    .stat-chip {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 8px 10px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 8px;
        min-width: 0;
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .stat-value {
        color: var(--text);
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 1.1rem;
        font-weight: 700;
    }

    /* ---------- Responsive ---------- */
    @media (max-width: 768px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
        .stat-row { grid-template-columns: 1fr; }
        [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
    }

    /* ---------- Scrollbars ---------- */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-badge">⚡ AI SEARCH LAB &amp; BENCHMARK SUITE</div>', unsafe_allow_html=True)
st.title("🔎 Word Search Puzzle AI Solver")
st.markdown(
    '<p class="section-lead">Generate puzzles, explore AI search algorithms, '
    'and compare their performance.</p>',
    unsafe_allow_html=True,
)


# -------------------- BENCHMARK LAB --------------------

st.divider()
st.header("📊 Benchmark Lab")
st.markdown(
    '<p class="section-lead">Compare DFS + Backtracking, Trie Search, and '
    'Optimized Trie Search on identical puzzles.</p>',
    unsafe_allow_html=True,
)

with st.expander("Configure and run benchmarks", expanded=True):
    config_col1, config_col2, config_col3 = st.columns([1, 1, 1])

    with config_col1:
        selected_grid_sizes = st.multiselect(
            "Grid sizes",
            options=[10, 15, 20],
            default=[10, 15, 20],
            key="benchmark_grid_sizes",
        )

    with config_col2:
        selected_word_counts = st.multiselect(
            "Target word counts",
            options=[5, 10, 15],
            default=[5, 10, 15],
            key="benchmark_word_counts",
        )

    with config_col3:
        benchmark_repeats = st.slider(
            "Repetitions per solver",
            min_value=1,
            max_value=10,
            value=5,
            key="benchmark_repeats",
        )

    run_benchmark_button = st.button(
        "🚀 Run Benchmark Experiments",
        type="primary",
        key="run_benchmark_experiments",
    )

    if run_benchmark_button:
        if not selected_grid_sizes or not selected_word_counts:
            st.warning(
                "Select at least one grid size and word count."
            )
        else:
            try:
                with st.spinner(
                    "Running experiments for all three solvers..."
                ):
                    results = run_benchmark(
                        grid_sizes=tuple(selected_grid_sizes),
                        word_counts=tuple(selected_word_counts),
                        repeats=benchmark_repeats,
                    )

                    csv_path = export_results_to_csv(
                        results,
                        "benchmark_results.csv",
                    )

                    chart_paths = generate_comparison_charts(
                        csv_path=csv_path,
                        output_dir="reports/benchmark_charts",
                    )

                st.session_state.benchmark_lab_results = results
                st.session_state.benchmark_lab_csv = str(csv_path)
                st.session_state.benchmark_lab_charts = [
                    str(path) for path in chart_paths
                ]

                st.success("Benchmark completed successfully!")

            except (ValueError, RuntimeError, OSError) as error:
                st.error(f"Benchmark failed: {error}")

# Display the latest saved benchmark results.
if st.session_state.get("benchmark_lab_results"):
    results = st.session_state.benchmark_lab_results
    results_df = pd.DataFrame(results)

    st.subheader("📈 Benchmark Results")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Experiments", len(results))
    metric2.metric(
        "Algorithms",
        results_df["algorithm"].nunique(),
    )
    metric3.metric(
        "All-words-found results",
        int(results_df["all_words_found"].sum()),
        f"out of {len(results_df)} runs",
    )

    display_columns = [
        "algorithm",
        "grid_size",
        "word_list_size",
        "repeats",
        "words_found",
        "total_words",
        "states_explored",
        "mean_time_ms",
        "median_time_ms",
        "all_words_found",
    ]

    st.dataframe(
        results_df[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "mean_time_ms": st.column_config.NumberColumn(
                "mean_time_ms", format="%.3f"
            ),
            "median_time_ms": st.column_config.NumberColumn(
                "median_time_ms", format="%.3f"
            ),
        },
    )

    csv_path = st.session_state.get("benchmark_lab_csv")

    if csv_path and Path(csv_path).exists():
        with open(csv_path, "rb") as csv_file:
            st.download_button(
                label="⬇️ Download Benchmark CSV",
                data=csv_file.read(),
                file_name="benchmark_results.csv",
                mime="text/csv",
                key="download_benchmark_csv",
            )

    st.subheader("📊 Comparison Charts")

    chart_paths = st.session_state.get(
        "benchmark_lab_charts", []
    )

    existing_charts = [
        chart_path for chart_path in chart_paths
        if Path(chart_path).exists()
    ]

    chart_labels = {
        "runtime_comparison": "⏱️ Runtime",
        "states_explored_comparison": "🧭 Search effort",
        "word_completion_comparison": "✅ Word-finding success",
    }

    if existing_charts:
        chart_tabs = st.tabs([
            chart_labels.get(
                Path(chart_path).stem,
                Path(chart_path).stem.replace("_", " ").title(),
            )
            for chart_path in existing_charts
        ])

        for chart_tab, chart_path in zip(chart_tabs, existing_charts):
            with chart_tab:
                st.image(chart_path, use_container_width=True)

st.divider()

# -------------------- END BENCHMARK LAB --------------------


SOLVERS = {
    "DFS + Backtracking": solve_dfs,
    "Trie Search": solve_trie,
    "Optimized Trie Search": solve_trie_optimized,
}

PRESETS = {
    "Programming": ["PYTHON", "JAVA", "CODING", "DEBUG", "SCRIPT"],
    "Animals": ["TIGER", "HORSE", "ZEBRA", "SNAKE", "EAGLE"],
    "Space": ["PLANET", "GALAXY", "COMET", "ORBIT", "STAR"],
}

# -------------------- GRID RENDERING --------------------

def render_grid(grid, state=None):
    """Render a letter grid with colors representing the search trace."""
    state = state or {}

    explored = state.get("explored_cells", set())
    matched = state.get("matched_cells", set())
    failed = state.get("failed_cells", set())
    current_path = set(state.get("current_path", []))
    found_words = state.get("found_words", {})

    found_cells = {
        tuple(position)
        for path in found_words.values()
        for position in path
    }

    cell_size = max(25, min(43, 420 // max(len(grid[0]), 1)))

    css = """
    <style>
    .ws-grid {
        display: grid;
        gap: 4px;
        width: fit-content;
        max-width: 100%;
        margin: 10px auto 18px auto;
        padding: 10px;
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(51, 65, 85, 0.55);
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    .ws-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        aspect-ratio: 1 / 1;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 7px;
        font-weight: 700;
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        letter-spacing: 0.5px;
        color: #f1f5f9;
        box-sizing: border-box;
        transition: transform 0.12s ease, background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .ws-plain {
        background: #151d2f;
        border-color: rgba(148, 163, 184, 0.2);
    }
    .ws-explored {
        background: #1e3a5f;
        border-color: #60a5fa;
        color: #93c5fd;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.35);
    }
    .ws-failed {
        background: #3f1d24;
        border-color: #f87171;
        color: #fca5a5;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.35);
    }
    .ws-matched {
        background: #3d2e0f;
        border-color: #fbbf24;
        color: #fde68a;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
    }
    .ws-current {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border: 2px solid #c4b5fd;
        color: #ffffff;
        box-shadow: 0 0 14px rgba(99, 102, 241, 0.65), inset 0 1px 1px rgba(255, 255, 255, 0.35);
        font-weight: 800;
    }
    .ws-found {
        background: linear-gradient(135deg, #047857 0%, #10b981 100%);
        border: 2px solid #6ee7b7;
        color: #ffffff;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.55), inset 0 1px 1px rgba(255, 255, 255, 0.3);
        font-weight: 800;
    }
    </style>
    """

    cells_html = []

    for row_index, row in enumerate(grid):
        for col_index, letter in enumerate(row):
            position = (row_index, col_index)

            # Highest priority first: permanently found words.
            if position in found_cells:
                cell_class = "ws-found"
            elif position in current_path:
                cell_class = "ws-current"
            elif position in matched:
                cell_class = "ws-matched"
            elif position in failed:
                cell_class = "ws-failed"
            elif position in explored:
                cell_class = "ws-explored"
            else:
                cell_class = "ws-plain"

            safe_letter = html.escape(str(letter))

            cells_html.append(
                f'<div class="ws-cell {cell_class}" '
                f'style="width:{cell_size}px;font-size:'
                f'{max(11, cell_size // 2)}px;">'
                f'{safe_letter}</div>'
            )

    grid_html = (
        f'<div class="ws-grid" '
        f'style="grid-template-columns:repeat({len(grid[0])}, '
        f'{cell_size}px);">'
        + "".join(cells_html)
        + "</div>"
    )

    st.markdown(css + grid_html, unsafe_allow_html=True)


def validate_selected_word(grid, selected_cells, target_words):
    """Validate a selection of grid cells against target words."""
    if not selected_cells:
        return None

    cells = sorted(set(
        (int(row), int(col)) for row, col in selected_cells
    ))

    if len(cells) == 1:
        row, col = cells[0]
        selected_word = grid[row][col]
    else:
        rows = [row for row, _ in cells]
        cols = [col for _, col in cells]

        row_diff = rows[-1] - rows[0]
        col_diff = cols[-1] - cols[0]

        # A valid word must follow one straight line.
        if row_diff != 0 and col_diff != 0:
            if abs(row_diff) != abs(col_diff):
                return None

        step_row = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        step_col = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)

        expected_cells = [
            (rows[0] + i * step_row, cols[0] + i * step_col)
            for i in range(len(cells))
        ]

        if set(expected_cells) != set(cells):
            return None

        selected_word = "".join(
            grid[row][col] for row, col in expected_cells
        )

    normalized_targets = {
        word.upper() for word in target_words
    }

    if selected_word in normalized_targets:
        return selected_word

    reverse_word = selected_word[::-1]
    if reverse_word in normalized_targets:
        return reverse_word

    return None


def describe_event(event):
    """Turn a trace event into a readable explanation."""
    event_type = event.get("type", "unknown")
    position = event.get("position")
    word = event.get("word")

    descriptions = {
        "start_word": f"Starting search for **{word}**.",
        "explore": f"Exploring cell **{position}**.",
        "match": f"A search path matches part of **{word or 'a target word'}**.",
        "backtrack": f"Backtracking from an unsuccessful path near **{position}**.",
        "word_found": f"Found the word **{word}**!",
        "word_not_found": f"Could not find **{word}** in the grid.",
    }

    return descriptions.get(
        event_type,
        f"Processing search event: `{event_type}`.",
    )


# -------------------- SIDEBAR --------------------

st.sidebar.header("Puzzle Settings")

grid_size = st.sidebar.slider(
    "Grid size",
    min_value=5,
    max_value=30,
    value=10,
)

word_input = st.sidebar.text_area(
    "Target words (one per line)",
    value="PYTHON\nSEARCH\nALGORITHM\nPUZZLE\nSTREAMLIT",
    height=150,
)

preset = st.sidebar.selectbox(
    "Or choose a preset",
    ["Custom", "Programming", "Animals", "Space"],
)

if preset != "Custom":
    words = PRESETS[preset]
else:
    words = [
        word.strip().upper()
        for word in word_input.splitlines()
        if word.strip()
    ]

words = list(dict.fromkeys(words))

generate_button = st.sidebar.button(
    "🎲 Generate Puzzle",
    type="primary",
    use_container_width=True,
)

# -------------------- SESSION STATE --------------------

defaults = {
    "puzzle": None,
    "solver_results": None,
    "evaluation_results": None,
    "trace_player": None,
    "trace_solver_name": None,
    "trace_playing": False,
    "game_started": False,
    "game_start_time": None,
    "elapsed_before_pause": 0.0,
    "manual_found_words": [],
    "manual_selection": [],
    "manual_found_paths": {},
    "game_completed": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if generate_button:
    if not words:
        st.sidebar.error("Please enter at least one target word.")
    else:
        try:
            puzzle = generate_puzzle(grid_size, words)

            st.session_state.puzzle = puzzle
            st.session_state.solver_results = None
            st.session_state.evaluation_results = None
            st.session_state.trace_player = None
            st.session_state.trace_solver_name = None
            st.session_state.trace_playing = False

            # Reset the game timer for the new puzzle
            st.session_state.game_running = False
            st.session_state.game_elapsed = 0.0
            st.session_state.game_last_start = None

            st.session_state.manual_found_words = []
            st.session_state.manual_selection = []

            st.session_state.manual_found_paths = {}

        except (ValueError, RuntimeError) as error:
            st.sidebar.error(f"Could not generate puzzle: {error}")

# -------------------- MAIN INTERFACE --------------------

if st.session_state.puzzle is None:
    st.info("Choose your settings and click **Generate Puzzle** to begin.")
    st.stop()

puzzle = st.session_state.puzzle
grid = puzzle["grid"]
target_words = puzzle["words"]

left, right = st.columns([3, 2])

with left:
    st.subheader("🧩 Word Search Grid")

    st.caption(
        f"Grid: {len(grid)} × {len(grid[0])} | "
        f"Target words: {len(target_words)}"
    )

    # Display an interactive grid for manual word selection.
    grid_dataframe = pd.DataFrame(grid)

    # Interactive grid with mouse-drag selection
    found_paths = list(
        st.session_state.manual_found_paths.values()
    )

    selected_cells = interactive_grid(
        grid=grid,
        found_paths=found_paths,
        key="manual_word_grid",
    )

    st.session_state.manual_selection = selected_cells or []

    if st.button("Check Selected Word", key="check_manual_word"):
        selected_word = validate_selected_word(
            grid,
            st.session_state.manual_selection,
            target_words,
        )

        if selected_word is None:
            st.warning("That selection is not a target word. Try again.")

        elif selected_word in st.session_state.manual_found_words:
            st.info(f"You already found {selected_word}.")

        else:
            st.session_state.manual_found_words.append(selected_word)

            # Save the coordinates of the word so its highlight persists.
            cells = st.session_state.manual_selection
            cells = [(int(row), int(col)) for row, col in cells]

            forward_word = "".join(grid[row][col] for row, col in cells)
            if forward_word == selected_word:
                found_path = cells
            else:
                found_path = list(reversed(cells))

            if "manual_found_paths" not in st.session_state:
                st.session_state.manual_found_paths = {}

            st.session_state.manual_found_paths[selected_word] = found_path
            st.success(f"🎉 Correct! You found {selected_word}.")

        # Stop the timer when the player finds every target word.
        if set(st.session_state.manual_found_words) >= set(target_words):
            if st.session_state.game_running:
                st.session_state.game_elapsed += (
                    time.perf_counter()
                    - st.session_state.game_last_start
                )
                st.session_state.game_running = False
                st.session_state.game_last_start = None

            st.session_state.game_completed = False

    found_count = len(st.session_state.manual_found_words)
    total_count = len(target_words)
    found_pct = (found_count / total_count * 100) if total_count else 0

    remaining_words = [
        word for word in target_words
        if word not in st.session_state.manual_found_words
    ]

    remaining_text = (
        ", ".join(html.escape(word) for word in remaining_words)
        if remaining_words else "None — puzzle complete!"
    )

    st.markdown(
        f"""
        <div class="progress-card">
            <div class="progress-head">
                <span>Words found: <strong>{found_count} / {total_count}</strong></span>
                <span class="muted">{found_pct:.0f}%</span>
            </div>
            <div class="progress-track" role="progressbar"
                 aria-valuenow="{found_count}" aria-valuemin="0"
                 aria-valuemax="{total_count}">
                <div class="progress-fill" style="width:{found_pct:.1f}%"></div>
            </div>
            <div class="progress-remaining"><strong>Remaining:</strong> {remaining_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if st.session_state.game_completed:
        final_seconds = st.session_state.game_elapsed
        minutes = int(final_seconds // 60)
        seconds = int(final_seconds % 60)

        st.success(
            f"🏆 Puzzle completed! Your final time: "
            f"{minutes:02d}:{seconds:02d}"
        )


    
    # -------------------- PLAYER TIMER --------------------

    st.subheader("⏱️ Your Challenge")

    if "game_running" not in st.session_state:
        st.session_state.game_running = False

    if "game_elapsed" not in st.session_state:
        st.session_state.game_elapsed = 0.0

    if "game_last_start" not in st.session_state:
        st.session_state.game_last_start = None

    timer_col1, timer_col2, timer_col3 = st.columns(3)

    with timer_col1:
        if st.button("▶️ Start / Resume", key="game_start"):
            if not st.session_state.game_running:
                st.session_state.game_last_start = time.perf_counter()
                st.session_state.game_running = True
                st.rerun()

    with timer_col2:
        if st.button("⏸️ Pause", key="game_pause"):
            if st.session_state.game_running:
                st.session_state.game_elapsed += (
                    time.perf_counter()
                    - st.session_state.game_last_start
                )
                st.session_state.game_running = False
                st.session_state.game_last_start = None
                st.rerun()

    with timer_col3:
        if st.button("🔄 Reset Timer", key="game_reset"):
            st.session_state.game_running = False
            st.session_state.game_elapsed = 0.0
            st.session_state.game_last_start = None
            st.rerun()

    # Refresh the app every second while the game timer is running.
    if st.session_state.game_running:
        st_autorefresh(
            interval=1000,
            limit=None,
            key="game_timer_refresh",
        )

    current_elapsed = st.session_state.game_elapsed

    if st.session_state.game_running:
        current_elapsed += (
            time.perf_counter() - st.session_state.game_last_start
        )

    minutes = int(current_elapsed // 60)
    seconds = int(current_elapsed % 60)

    st.metric("Elapsed Time", f"{minutes:02d}:{seconds:02d}")

    if st.session_state.game_running:
        st.caption("Timer running. Interact with the app to refresh the display.")

with right:
    st.subheader("📚 Target Words")

    found_set = set(st.session_state.manual_found_words)
    words_badges = []
    for word in target_words:
        is_found = word in found_set
        badge_cls = "target-word-badge found" if is_found else "target-word-badge pending"
        icon = "✓" if is_found else "▫"
        words_badges.append(
            f'<div class="{badge_cls}"><span>{icon}</span> <span>{html.escape(word)}</span></div>'
        )

    st.markdown(
        f'<div class="target-words-grid">{"".join(words_badges)}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.subheader("🤖 AI Solver")

    selected_solver = st.selectbox(
        "Choose an algorithm",
        list(SOLVERS.keys()),
        key="selected_solver",
    )

    if st.button("🚀 Solve Puzzle", type="primary"):
        result = SOLVERS[selected_solver](grid, target_words)

        st.session_state.solver_results = result
        st.session_state.trace_player = TracePlayer(result["events"])
        st.session_state.trace_solver_name = selected_solver
        st.session_state.trace_playing = False

    if st.button("📊 Compare All Solvers"):
        st.session_state.evaluation_results = evaluate_solvers(
            grid, target_words
        )

# -------------------- SOLVER RESULTS --------------------

result = st.session_state.solver_results

if result is not None:
    st.divider()
    st.subheader(f"✅ Results: {result['algorithm']}")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Words Found",
        len(result["found_words"]),
        f"out of {len(target_words)}",
    )

    metric2.metric("States Explored", f"{result['states_explored']:,}")

    metric3.metric(
        "Execution Time",
        f"{result['execution_time'] * 1000:.3f} ms",
    )

    if result["found_words"]:
        found_badges = "".join(
            f'<span class="target-word-badge found"><span>✓</span> '
            f'<span>{html.escape(word)}</span></span>'
            for word in result["found_words"]
        )
        st.markdown(
            f'<div class="inline-label">Found words</div>'
            f'<div class="target-words-grid">{found_badges}</div>',
            unsafe_allow_html=True,
        )

    if result["missing_words"]:
        st.warning(
            "Words not found: " + ", ".join(result["missing_words"])
        )

    with st.expander("View word coordinates"):
        st.caption("Coordinates use zero-based (row, column) indexing.")

        for word, path in result["placements"].items():
            st.markdown(f"**{word}** · `{path}`")

    # -------------------- ANIMATION --------------------

    st.divider()
    st.subheader("🎬 Animated Search Playback")
    st.caption(
        "Step through the actual recorded search events to see "
        "how the selected algorithm explores the grid."
    )

    player = st.session_state.trace_player

    if player is not None:
        state = player.get_state()

        control1, control2, control3, control4 = st.columns(4)

        with control1:
            if st.button("⏮ Previous", use_container_width=True):
                st.session_state.trace_playing = False
                player.step_backward()
                st.rerun()

        with control2:
            if st.button("⏭ Next Step", use_container_width=True):
                st.session_state.trace_playing = False
                player.step_forward()
                st.rerun()

        with control3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.trace_playing = False
                player.reset()
                st.rerun()

        with control4:
            if st.button(
                "▶️ Play" if not st.session_state.trace_playing else "⏸ Pause",
                use_container_width=True,
            ):
                st.session_state.trace_playing = (
                    not st.session_state.trace_playing
                )
                st.rerun()


        # Automatically request reruns while playback is active.
        if st.session_state.trace_playing and not player.is_finished:
            st_autorefresh(
                interval=250,
                limit=None,
                key="search_trace_refresh",
            )
            player.step_forward()

        if player.is_finished:
            st.session_state.trace_playing = False

        state = player.get_state()

        progress = (
            state["step"] / state["total_steps"]
            if state["total_steps"] > 0
            else 1.0
        )

        st.progress(progress)
        st.caption(
            f"Step {state['step']} of {state['total_steps']}"
        )

        st.markdown(
            """
            <div class="legend-bar" aria-label="Search playback legend">
                <span class="legend-pill pill-explored"><span class="legend-dot dot-explored"></span>Explored</span>
                <span class="legend-pill pill-backtracked"><span class="legend-dot dot-backtracked"></span>Backtracked</span>
                <span class="legend-pill pill-matched"><span class="legend-dot dot-matched"></span>Matched</span>
                <span class="legend-pill pill-active"><span class="legend-dot dot-active"></span>Active path</span>
                <span class="legend-pill pill-found"><span class="legend-dot dot-found"></span>Found word</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        animation_left, animation_right = st.columns([3, 2])

        with animation_left:
            render_grid(grid, state)

        with animation_right:
            st.markdown(
                '<div class="inline-label">What is happening?</div>',
                unsafe_allow_html=True,
            )

            if state["last_event"] is not None:
                # describe_event() returns Markdown; inside an HTML block
                # Markdown is not parsed, so convert **bold** to <strong>.
                event_html = re.sub(
                    r"\*\*(.+?)\*\*",
                    r"<strong>\1</strong>",
                    html.escape(describe_event(state["last_event"])),
                )
                event_html = re.sub(r"`(.+?)`", r"<code>\1</code>", event_html)
                st.markdown(
                    f'<div class="event-card">{event_html}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("Press Next Step or Play to start the animation.")

            st.markdown(
                f"""
                <div class="stat-row">
                    <div class="stat-chip"><span class="stat-label">Explored cells</span>
                        <span class="stat-value">{len(state['explored_cells']):,}</span></div>
                    <div class="stat-chip"><span class="stat-label">Matched cells</span>
                        <span class="stat-value">{len(state['matched_cells']):,}</span></div>
                    <div class="stat-chip"><span class="stat-label">Words discovered</span>
                        <span class="stat-value">{len(state['found_words']):,}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if state["found_words"]:
                discovered_badges = "".join(
                    f'<span class="target-word-badge found"><span>✓</span> '
                    f'<span>{html.escape(str(word))}</span></span>'
                    for word in state["found_words"]
                )
                st.markdown(
                    f'<div class="inline-label">Discovered words</div>'
                    f'<div class="target-words-grid">{discovered_badges}</div>',
                    unsafe_allow_html=True,
                )

        if player.is_finished:
            st.success("Search trace complete!")

        elif st.session_state.trace_playing:
            st.caption("Playing… the next event will appear automatically.")

# -------------------- PERFORMANCE COMPARISON --------------------

if st.session_state.evaluation_results is not None:
    st.divider()
    st.subheader("📊 Algorithm Performance Comparison")

    summary = get_evaluation_summary(
        st.session_state.evaluation_results
    )

    dataframe = pd.DataFrame(summary)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown(
            '<div class="inline-label">Execution time comparison</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(
            dataframe.set_index("Algorithm")["Execution Time (ms)"],
            height=240,
            color="#6366F1",
        )

    with chart_col2:
        st.markdown(
            '<div class="inline-label">Search states comparison</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(
            dataframe.set_index("Algorithm")["States Explored"],
            height=240,
            color="#38BDF8",
        )
