# Word Search Puzzle AI Solver

An interactive AI-based word search puzzle application built with Python and Streamlit. The project demonstrates and compares three search strategies: **DFS with Backtracking, Trie Search, and Optimized Trie Search**.

Users can generate word search puzzles, solve them manually or with AI, visualize the search process, and compare algorithm performance using execution time and search effort metrics.

## 1. Project Objectives

- Implement and compare three AI search algorithms for word search puzzles.
- Demonstrate Depth-First Search (DFS), backtracking, and Trie-based prefix matching.
- Visualize the search process through animated traces.
- Provide an interactive interface for manually solving puzzles.
- Evaluate algorithms using execution time, states explored, and words found.
- Generate benchmark reports, CSV files, and comparison charts.

## 2. Features

- **Puzzle generation:** Generate word search grids with configurable sizes and target word lists.
- **Multiple algorithms:** Choose between DFS with Backtracking, Trie Search, and Optimized Trie Search.
- **Eight-direction search:** Find words horizontally, vertically, and diagonally, in both forward and reverse directions.
- **Interactive gameplay:** Select words by dragging across grid cells, including diagonal selections.
- **Progress tracking:** View the target word list, highlight discovered words, and track completion time.
- **AI visualization:** Play, pause, step through, and reset the animated search trace.
- **Performance evaluation:** Compare execution time, states explored, and word-finding results.
- **Benchmark Lab:** Run repeated experiments on identical puzzles for all three algorithms.
- **Data export:** Export benchmark results to CSV and generate comparison charts.

## 3. Algorithms

### 3.1 DFS with Backtracking

Depth-First Search explores possible paths through the letter grid. For each target word, the algorithm explores candidate starting positions and follows valid neighboring cells in a straight line. Backtracking allows the search to abandon unsuccessful paths and continue exploring alternatives.

### 3.2 Trie Search

A Trie is a tree-based data structure that stores words through shared prefixes. Instead of treating every target word independently, the solver uses the Trie to identify valid prefixes while exploring the grid. Paths that cannot match a Trie prefix can be abandoned early.

### 3.3 Optimized Trie Search

The optimized version improves Trie-guided search by reducing unnecessary exploration using techniques such as indexing possible starting positions by their letters and pruning completed Trie branches, as implemented in the project.

The three algorithms are evaluated using the same puzzle configurations to make their results more comparable.

## 4. Technology Stack

- **Programming language:** Python
- **User interface:** Streamlit
- **Data analysis:** Pandas
- **Visualization:** Matplotlib
- **Testing:** Pytest
- **Version control:** Git and GitHub

## 5. Project Structure

```text
word-search-puzzle-ai-solver/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── puzzle_generator.py
│   ├── trie.py
│   ├── dfs_solver.py
│   ├── trie_solver.py
│   ├── animation.py
│   ├── evaluation.py
│   ├── benchmark.py
│   ├── export_results.py
│   └── plot_results.py
├── tests/
│   ├── test_trie.py
│   ├── test_solvers.py
│   ├── test_puzzle_generator.py
│   ├── test_trie_solver.py
│   ├── test_animation.py
│   ├── test_benchmark.py
│   ├── test_export_results.py
│   └── test_plot_results.py
├── data/
│   └── sample_puzzles.json
├── docs/
│   └── screenshots/
└── components/
    └── interactive_grid/
        ├── __init__.py
        └── index.html
```

## 6. Installation and Setup

### Prerequisites

- Python installed
- pip package manager
- Git (optional, for version control)

### Step 1: Clone the repository

```bash
git clone https://github.com/harshkdm31/word-search-puzzle-ai-solver.git
cd word-search-puzzle-ai-solver
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Launch the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to use the application.

## 7. Benchmarking and Evaluation

The Benchmark Lab compares all three solvers on the same generated puzzle for each experiment configuration. Each solver is executed repeatedly to reduce the influence of individual timing variations.

### Evaluation metrics

| Metric | Description |
|---|---|
| Execution time | Time taken by the solver to complete its search |
| States explored | Number of search states explored, according to the solver's implementation |
| Words found | Number of target words successfully identified |
| Total words | Number of target words supplied to the solver |
| Completion rate | Percentage of target words found |
| Grid size | Dimensions of the puzzle grid |
| Word-list size | Number of target words in the experiment |

### Generated outputs

The benchmark workflow generates:

- `benchmark_results.csv` — tabular benchmark data.
- `reports/benchmark_charts/runtime_comparison.png` — execution-time comparison.
- `reports/benchmark_charts/states_explored_comparison.png` — search-effort comparison.
- `reports/benchmark_charts/word_completion_comparison.png` — word-finding completion comparison.

These outputs can be used to examine the trade-offs between the three search strategies.

## 8. Running Tests

Run the complete test suite from the project root:

```bash
python -m pytest -v
```

The tests cover the Trie, solvers, puzzle generation, animation, benchmarking, CSV export, and chart generation.

## 9. Design Scope and Limitations

This project is designed as an educational AI mini-project. It runs locally and does not require a backend server, database, or user authentication system.

The benchmark results depend on the tested puzzle configurations, implementation details, and execution environment. Runtime differences should therefore be interpreted alongside the number of states explored and the number of words found.

The application demonstrates algorithmic search and empirical comparison; it is not intended to be a comprehensive benchmarking framework.

## 10. Conclusion

The Word Search Puzzle AI Solver combines an interactive puzzle game with practical implementations of DFS, backtracking, and Trie-based search. Animated traces help explain how the algorithms explore the grid, while benchmark tables and charts provide a way to compare their performance.

The project demonstrates the application of fundamental AI search techniques, data structures, visualization, and experimental evaluation in a single interactive application.
