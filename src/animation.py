
class TracePlayer:
    """Replay recorded search events forward and backward."""

    def __init__(self, events):
        self.events = list(events)
        self.index = 0
        self.reset()

    def reset(self):
        """Return the playback state to its initial position."""
        self.index = 0
        self.explored_cells = set()
        self.matched_cells = set()
        self.failed_cells = set()
        self.found_words = {}
        self.current_position = None
        self.current_path = []
        self.last_event = None

    @property
    def total_steps(self):
        return len(self.events)

    @property
    def is_finished(self):
        return self.index >= self.total_steps

    def _apply_event(self, event):
        """Update the displayed state using one event."""
        event_type = event.get("type")
        position = event.get("position")
        path = event.get("path", [])

        self.last_event = event
        self.current_path = list(path)

        if position is not None:
            self.current_position = tuple(position)

        if event_type == "explore":
            if position is not None:
                self.explored_cells.add(tuple(position))

        elif event_type == "match":
            self.matched_cells.update(tuple(cell) for cell in path)

        elif event_type == "backtrack":
            self.failed_cells.update(tuple(cell) for cell in path)

        elif event_type == "word_found":
            word = event.get("word")
            if word:
                self.found_words[word] = [
                    tuple(cell) for cell in path
                ]

    def step_forward(self):
        """Apply the next event. Return None when finished."""
        if self.is_finished:
            return None

        event = self.events[self.index]
        self._apply_event(event)
        self.index += 1
        return event

    def step_backward(self):
        """Undo one step by rebuilding the previous state."""
        if self.index == 0:
            return None

        self.index -= 1
        target_index = self.index

        self.reset()

        for _ in range(target_index):
            self.step_forward()

        return self.last_event

    def get_state(self):
        """Return a snapshot suitable for GUI rendering."""
        return {
            "step": self.index,
            "total_steps": self.total_steps,
            "is_finished": self.is_finished,
            "current_position": self.current_position,
            "current_path": list(self.current_path),
            "explored_cells": set(self.explored_cells),
            "matched_cells": set(self.matched_cells),
            "failed_cells": set(self.failed_cells),
            "found_words": {
                word: list(path)
                for word, path in self.found_words.items()
            },
            "last_event": self.last_event,
        }
