
import time

from src.puzzle_generator import DIRECTIONS


def solve_dfs(grid, words):
    """
    Find target words independently using DFS and backtracking.

    Words must appear in a straight line in one of the eight
    directions. Returns coordinates and search-event records.
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

    for word in words:
        if not isinstance(word, str):
            raise ValueError("Every target word must be text.")

        word = "".join(word.split()).upper()

        if not word or not word.isascii() or not word.isalpha():
            raise ValueError(f"Invalid target word: {word!r}")

        if word not in seen:
            targets.append(word)
            seen.add(word)

    events = []
    placements = {}
    states_explored = 0

    def record(event_type, **details):
        events.append({"type": event_type, **details})

    def search_from(word, index, row, col, dr, dc, path):
        """Recursively match a word along one straight direction."""
        nonlocal states_explored

        if not (0 <= row < rows and 0 <= col < cols):
            record(
                "backtrack",
                word=word,
                position=(row, col),
                reason="out_of_bounds",
                path=path.copy(),
            )
            return None

        states_explored += 1
        position = (row, col)

        record(
            "explore",
            word=word,
            position=position,
            letter=grid[row][col],
            path=path.copy(),
        )

        if grid[row][col] != word[index]:
            record(
                "backtrack",
                word=word,
                position=position,
                reason="letter_mismatch",
                path=path.copy(),
            )
            return None

        current_path = path + [position]

        record(
            "match",
            word=word,
            position=position,
            path=current_path.copy(),
        )

        if index == len(word) - 1:
            record(
                "word_found",
                word=word,
                path=current_path.copy(),
            )
            return current_path

        result = search_from(
            word,
            index + 1,
            row + dr,
            col + dc,
            dr,
            dc,
            current_path,
        )

        if result is None:
            record(
                "backtrack",
                word=word,
                position=position,
                reason="continuation_failed",
                path=current_path.copy(),
            )

        return result

    start_time = time.perf_counter()

    for word in targets:
        found_path = None

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] != word[0]:
                    continue

                record(
                    "start_word",
                    word=word,
                    position=(row, col),
                )

                for dr, dc in DIRECTIONS:
                    found_path = search_from(
                        word, 0, row, col, dr, dc, []
                    )

                    if found_path is not None:
                        break

                if found_path is not None:
                    break

        if found_path is not None:
            placements[word] = found_path
        else:
            record("word_not_found", word=word)

    elapsed_seconds = time.perf_counter() - start_time

    return {
        "algorithm": "DFS + Backtracking",
        "found_words": list(placements.keys()),
        "missing_words": [
            word for word in targets if word not in placements
        ],
        "placements": placements,
        "states_explored": states_explored,
        "execution_time": elapsed_seconds,
        "events": events,
    }
