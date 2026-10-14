
import streamlit as st
import pandas as pd

from src.puzzle_generator import generate_puzzle
from src.dfs_solver import solve_dfs
from src.trie_solver import solve_trie, solve_trie_optimized
from src.evaluation import evaluate_solvers, get_evaluation_summary

st.set_page_config(
    page_title="Word Search Puzzle AI Solver",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Word Search Puzzle AI Solver")
st.write(
    "Generate word-search puzzles, explore AI search algorithms, "
    "and compare their performance."
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

presets = {
    "Programming": [
        "PYTHON", "JAVA", "CODING", "DEBUG", "SCRIPT"
    ],
    "Animals": [
        "TIGER", "HORSE", "ZEBRA", "SNAKE", "EAGLE"
    ],
    "Space": [
        "PLANET", "GALAXY", "COMET", "ORBIT", "STAR"
    ],
}

if preset != "Custom":
    words = presets[preset]
    st.sidebar.caption(f"{len(words)} preset words selected.")
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

if "puzzle" not in st.session_state:
    st.session_state.puzzle = None

if "solver_results" not in st.session_state:
    st.session_state.solver_results = None

if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None

if "selected_solver" not in st.session_state:
    st.session_state.selected_solver = "DFS + Backtracking"

# -------------------- GENERATE PUZZLE --------------------

if generate_button:
    if not words:
        st.sidebar.error("Please enter at least one target word.")
    else:
        try:
            puzzle = generate_puzzle(grid_size, words)

            st.session_state.puzzle = puzzle
            st.session_state.solver_results = None
            st.session_state.evaluation_results = None

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
    st.subheader("🧩 Puzzle Grid")

    st.caption(
        f"Grid: {len(grid)} × {len(grid[0])} | "
        f"Target words: {len(target_words)}"
    )

    grid_text = "\n".join(
        " ".join(row) for row in grid
    )

    st.code(grid_text, language=None)

with right:
    st.subheader("📚 Find These Words")

    for word in target_words:
        st.write(f"▫️ {word}")

    st.divider()
    st.subheader("🤖 AI Solver")

    solver_options = {
        "DFS + Backtracking": solve_dfs,
        "Trie Search": solve_trie,
        "Optimized Trie Search": solve_trie_optimized,
    }

    selected_solver = st.selectbox(
        "Choose an algorithm",
        list(solver_options.keys()),
        key="selected_solver",
    )

    if st.button("🚀 Solve Puzzle", type="primary"):
        result = solver_options[selected_solver](grid, target_words)
        st.session_state.solver_results = result

    if st.button("📊 Compare All Solvers"):
        st.session_state.evaluation_results = evaluate_solvers(
            grid, target_words
        )

# -------------------- SOLVER RESULTS --------------------

if st.session_state.solver_results is not None:
    result = st.session_state.solver_results

    st.divider()
    st.subheader(f"✅ Results: {result['algorithm']}")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Words Found",
        len(result["found_words"]),
        f"out of {len(target_words)}",
    )

    metric2.metric(
        "States Explored",
        result["states_explored"],
    )

    metric3.metric(
        "Execution Time",
        f"{result['execution_time'] * 1000:.3f} ms",
    )

    if result["found_words"]:
        st.write("**Found words:** " + ", ".join(result["found_words"]))

    if result["missing_words"]:
        st.warning(
            "Words not found: " + ", ".join(result["missing_words"])
        )

    with st.expander("View word coordinates"):
        st.caption("Coordinates are zero-based: (row, column).")

        for word, path in result["placements"].items():
            st.write(f"**{word}:** {path}")

# -------------------- PERFORMANCE COMPARISON --------------------

if st.session_state.evaluation_results is not None:
    st.divider()
    st.subheader("📊 Algorithm Performance Comparison")

    summary = get_evaluation_summary(
        st.session_state.evaluation_results
    )

    dataframe = pd.DataFrame(summary)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    chart_data = dataframe.set_index("Algorithm")[
        ["Execution Time (ms)", "States Explored"]
    ]

    st.write("**Execution time comparison**")
    st.bar_chart(dataframe.set_index("Algorithm")["Execution Time (ms)"])

    st.write("**Search states comparison**")
    st.bar_chart(dataframe.set_index("Algorithm")["States Explored"])
