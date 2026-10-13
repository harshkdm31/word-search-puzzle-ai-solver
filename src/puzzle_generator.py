
import random
import string


# Eight possible directions: horizontal, vertical, and diagonal.
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),             (0, 1),
    (1, -1),  (1, 0),    (1, 1),
]

MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 30


def generate_puzzle(grid_size, words, seed=None):
    """
    Generate a word-search puzzle.

    Returns a dictionary containing:
        grid: 2D list of uppercase letters
        words: normalized target words
        placements: coordinates of each placed word

    Coordinates use zero-based (row, column) indexing.
    """
    if not isinstance(grid_size, int) or isinstance(grid_size, bool):
        raise ValueError("Grid size must be an integer.")

    if not MIN_GRID_SIZE <= grid_size <= MAX_GRID_SIZE:
        raise ValueError(
            f"Grid size must be between "
            f"{MIN_GRID_SIZE} and {MAX_GRID_SIZE}."
        )

    if not words:
        raise ValueError("Please provide at least one target word.")

    # Normalize words and remove duplicates while preserving order.
    normalized_words = []
    seen = set()

    for word in words:
        if not isinstance(word, str):
            raise ValueError("Every target word must be text.")

        cleaned = "".join(word.split()).upper()

        if not cleaned or not cleaned.isalpha() or not cleaned.isascii():
            raise ValueError(
                f"Invalid word: {word!r}. "
                "Use English letters only."
            )

        if len(cleaned) > grid_size:
            raise ValueError(
                f"'{cleaned}' is longer than the {grid_size}x{grid_size} grid."
            )

        if cleaned not in seen:
            normalized_words.append(cleaned)
            seen.add(cleaned)

    if not normalized_words:
        raise ValueError("Please provide at least one valid word.")

    rng = random.Random(seed)

    # Place longer words first to make placement easier.
    placement_order = sorted(
        normalized_words,
        key=lambda word: len(word),
        reverse=True,
    )

    grid = [["" for _ in range(grid_size)]
            for _ in range(grid_size)]

    placements = {}

    def get_candidate_cells(word):
        """Return all valid starting positions and directions."""
        candidates = []

        for row in range(grid_size):
            for col in range(grid_size):
                for dr, dc in DIRECTIONS:
                    end_row = row + (len(word) - 1) * dr
                    end_col = col + (len(word) - 1) * dc

                    if not (
                        0 <= end_row < grid_size
                        and 0 <= end_col < grid_size
                    ):
                        continue

                    coordinates = [
                        (row + i * dr, col + i * dc)
                        for i in range(len(word))
                    ]

                    # Overlapping words may share matching letters.
                    if all(
                        grid[r][c] in ("", letter)
                        for (r, c), letter in zip(coordinates, word)
                    ):
                        candidates.append(coordinates)

        rng.shuffle(candidates)
        return candidates

    def place_words(index):
        """Place all words using backtracking if necessary."""
        if index == len(placement_order):
            return True

        word = placement_order[index]

        for coordinates in get_candidate_cells(word):
            # Save previous cells so overlapping letters can be restored.
            previous = [grid[r][c] for r, c in coordinates]

            for (r, c), letter in zip(coordinates, word):
                grid[r][c] = letter

            placements[word] = coordinates

            if place_words(index + 1):
                return True

            # This placement failed; undo it.
            for (r, c), old_letter in zip(coordinates, previous):
                grid[r][c] = old_letter

            del placements[word]

        return False

    if not place_words(0):
        raise ValueError(
            "Could not place all words in this grid. "
            "Try a larger grid or fewer words."
        )

    # Fill every unused cell with a random uppercase letter.
    for row in range(grid_size):
        for col in range(grid_size):
            if grid[row][col] == "":
                grid[row][col] = rng.choice(string.ascii_uppercase)

    return {
        "grid": grid,
        "words": normalized_words,
        "placements": placements,
    }
