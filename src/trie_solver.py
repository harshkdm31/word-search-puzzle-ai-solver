
import time

from src.puzzle_generator import DIRECTIONS
from src.trie import Trie


def solve_trie(grid, words):
    """
    Find target words using Trie-guided directional search.

    Each grid cell is considered as a starting point. The solver
    follows each of the eight directions while the letters match
    a valid prefix in the Trie.
    """
    if not grid or not grid[0]:
        raise ValueError("Grid cannot be empty.")

    rows = len(grid)
    cols = len(grid[0])

    if any(len(row) != cols for row in grid):
        raise ValueError("Grid must be rectangular.")

    grid = [
        [str(cell).upper() for cell in row]
        for row in grid
    ]

    targets = []
    seen = set()

    trie = Trie()

    for word in words:
        if not isinstance(word, str):
            raise ValueError("Every target word must be text.")

        word = "".join(word.split()).upper()

        if not word or not word.isascii() or not word.isalpha():
            raise ValueError(f"Invalid target word: {word!r}")

        if word not in seen:
            targets.append(word)
            seen.add(word)
            trie.insert(word)

    events = []
    placements = {}
    states_explored = 0

    def record(event_type, **details):
        events.append({"type": event_type, **details})

    start_time = time.perf_counter()

    for row in range(rows):
        for col in range(cols):

            # If no target word starts with this letter,
            # there is no reason to search from this cell.
            first_letter = grid[row][col]

            if first_letter not in trie.root.children:
                continue

            record(
                "start_search",
                position=(row, col),
                letter=first_letter,
            )

            for dr, dc in DIRECTIONS:
                current_row = row
                current_col = col
                node = trie.root
                path = []
                prefix = ""

                while (
                    0 <= current_row < rows
                    and 0 <= current_col < cols
                ):
                    letter = grid[current_row][current_col]
                    position = (current_row, current_col)

                    states_explored += 1

                    record(
                        "explore",
                        position=position,
                        letter=letter,
                        path=path.copy(),
                    )

                    # Stop if this letter cannot extend the
                    # current prefix into any target word.
                    if letter not in node.children:
                        record(
                            "backtrack",
                            position=position,
                            reason="no_matching_prefix",
                            path=path.copy(),
                        )
                        break

                    node = node.children[letter]
                    prefix += letter
                    path.append(position)

                    record(
                        "match",
                        prefix=prefix,
                        position=position,
                        path=path.copy(),
                    )

                    if node.is_word:
                        record(
                            "word_found",
                            word=prefix,
                            path=path.copy(),
                        )

                        # Preserve the first occurrence found.
                        if prefix not in placements:
                            placements[prefix] = path.copy()

                    current_row += dr
                    current_col += dc

                else:
                    # The direction ended at the grid boundary.
                    record(
                        "backtrack",
                        position=(current_row, current_col),
                        reason="out_of_bounds",
                        path=path.copy(),
                    )

    elapsed_seconds = time.perf_counter() - start_time

    return {
        "algorithm": "Trie-Guided Search",
        "found_words": [
            word for word in targets if word in placements
        ],
        "missing_words": [
            word for word in targets if word not in placements
        ],
        "placements": placements,
        "states_explored": states_explored,
        "execution_time": elapsed_seconds,
        "events": events,
    }
