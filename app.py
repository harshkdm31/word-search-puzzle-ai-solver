
import time
import html

import pandas as pd
import streamlit as st

from src.puzzle_generator import generate_puzzle
from src.dfs_solver import solve_dfs
from src.trie_solver import solve_trie, solve_trie_optimized
from src.evaluation import evaluate_solvers, get_evaluation_summary
from src.animation import TracePlayer
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Word Search Puzzle AI Solver",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Word Search Puzzle AI Solver")
st.write(
    "Generate puzzles, explore AI search algorithms, "
    "and compare their performance."
)

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
        gap: 3px;
        width: fit-content;
        max-width: 100%;
        margin: 8px auto 16px auto;
    }
    .ws-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        aspect-ratio: 1 / 1;
        border: 1px solid #CBD5E1;
        border-radius: 5px;
        font-weight: 700;
        font-family: monospace;
        color: #1E293B;
        box-sizing: border-box;
    }
    .ws-plain { background: #F8FAFC; }
    .ws-explored { background: #DBEAFE; border-color: #60A5FA; }
    .ws-failed { background: #FEE2E2; border-color: #F87171; }
    .ws-matched { background: #FEF3C7; border-color: #F59E0B; }
    .ws-current { background: #C4B5FD; border: 2px solid #7C3AED; }
    .ws-found { background: #BBF7D0; border: 2px solid #16A34A; }
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

    render_grid(grid)

    st.caption(
        "Legend: 🔵 Explored · 🔴 Backtracked · "
        "🟡 Matched · 🟣 Active path · 🟢 Found word"
    )

with right:
    st.subheader("📚 Target Words")

    for word in target_words:
        st.write(f"▫️ {word}")

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

    metric2.metric("States Explored", result["states_explored"])

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
        st.caption("Coordinates use zero-based (row, column) indexing.")

        for word, path in result["placements"].items():
            st.write(f"**{word}:** {path}")

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

        animation_left, animation_right = st.columns([3, 2])

        with animation_left:
            render_grid(grid, state)

        with animation_right:
            st.markdown("**What is happening?**")

            if state["last_event"] is not None:
                st.markdown(describe_event(state["last_event"]))
            else:
                st.info("Press Next Step or Play to start the animation.")

            st.write(f"Explored cells: **{len(state['explored_cells'])}**")
            st.write(f"Matched cells: **{len(state['matched_cells'])}**")
            st.write(f"Words discovered: **{len(state['found_words'])}**")

            if state["found_words"]:
                st.write("**Discovered words:**")
                for word in state["found_words"]:
                    st.write(f"✅ {word}")

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

    st.write("**Execution time comparison**")
    st.bar_chart(
        dataframe.set_index("Algorithm")["Execution Time (ms)"]
    )

    st.write("**Search states comparison**")
    st.bar_chart(
        dataframe.set_index("Algorithm")["States Explored"]
    )
