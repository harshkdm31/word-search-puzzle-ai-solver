
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


def solve_trie_optimized(grid, words):
    """
    Optimized Trie-guided word search.

    Improvements:
    1. Index grid cells by letter to filter starting positions.
    2. Track remaining target words under each Trie node.
    3. Prune Trie branches when all words below them are found.
    """
    import time

    from collections import defaultdict

    from src.puzzle_generator import DIRECTIONS
    from src.trie import Trie

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

    trie = Trie()

    for word in targets:
        trie.insert(word)

    # Count how many target words exist below each Trie node.
    remaining = {}

    def count_words(node):
        count = int(node.is_word)

        for child in node.children.values():
            count += count_words(child)

        remaining[id(node)] = count
        return count

    count_words(trie.root)

    # Index all grid cells by their letter.
    cells_by_letter = defaultdict(list)

    for row in range(rows):
        for col in range(cols):
            cells_by_letter[grid[row][col]].append((row, col))

    events = []
    placements = {}
    states_explored = 0

    def record(event_type, **details):
        events.append({"type": event_type, **details})

    start_time = time.perf_counter()

    # Only visit cells matching the first letter of a target word.
    starting_letters = set(trie.root.children)

    for first_letter in starting_letters:
        for row, col in cells_by_letter.get(first_letter, []):

            if remaining[id(trie.root)] == 0:
                break

            record(
                "start_search",
                position=(row, col),
                letter=first_letter,
            )

            for dr, dc in DIRECTIONS:
                if remaining[id(trie.root)] == 0:
                    break

                current_row = row
                current_col = col
                node = trie.root
                path = []
                visited_nodes = [trie.root]
                prefix = ""

                while (
                    0 <= current_row < rows
                    and 0 <= current_col < cols
                ):
                    if remaining[id(node)] == 0:
                        record(
                            "backtrack",
                            position=(current_row, current_col),
                            reason="branch_already_solved",
                            path=path.copy(),
                        )
                        break

                    letter = grid[current_row][current_col]
                    position = (current_row, current_col)
                    states_explored += 1

                    record(
                        "explore",
                        position=position,
                        letter=letter,
                        path=path.copy(),
                    )

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
                    visited_nodes.append(node)

                    record(
                        "match",
                        prefix=prefix,
                        position=position,
                        path=path.copy(),
                    )

                    if node.is_word and prefix not in placements:
                        placements[prefix] = path.copy()

                        # This word has now been discovered.
                        # Reduce the count along its Trie path.
                        for visited_node in visited_nodes:
                            remaining[id(visited_node)] -= 1

                        record(
                            "word_found",
                            word=prefix,
                            path=path.copy(),
                        )

                    if remaining[id(node)] == 0:
                        record(
                            "backtrack",
                            position=position,
                            reason="branch_completed",
                            path=path.copy(),
                        )
                        break

                    current_row += dr
                    current_col += dc

                else:
                    record(
                        "backtrack",
                        position=(current_row, current_col),
                        reason="out_of_bounds",
                        path=path.copy(),
                    )

    elapsed_seconds = time.perf_counter() - start_time

    for word in targets:
        if word not in placements:
            record("word_not_found", word=word)

    return {
        "algorithm": "Optimized Trie Search",
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
