
from src.animation import TracePlayer


SAMPLE_EVENTS = [
    {
        "type": "explore",
        "position": (0, 0),
        "letter": "C",
        "path": [],
    },
    {
        "type": "match",
        "position": (0, 0),
        "prefix": "C",
        "path": [(0, 0)],
    },
    {
        "type": "explore",
        "position": (0, 1),
        "letter": "A",
        "path": [(0, 0)],
    },
    {
        "type": "match",
        "position": (0, 1),
        "prefix": "CA",
        "path": [(0, 0), (0, 1)],
    },
    {
        "type": "word_found",
        "word": "CAT",
        "path": [(0, 0), (0, 1), (0, 2)],
    },
    {
        "type": "backtrack",
        "position": (1, 0),
        "reason": "letter_mismatch",
        "path": [(1, 0)],
    },
]


def test_initial_state():
    player = TracePlayer(SAMPLE_EVENTS)
    state = player.get_state()

    assert state["step"] == 0
    assert state["total_steps"] == len(SAMPLE_EVENTS)
    assert not state["explored_cells"]
    assert not state["found_words"]


def test_step_forward():
    player = TracePlayer(SAMPLE_EVENTS)

    event = player.step_forward()
    state = player.get_state()

    assert event["type"] == "explore"
    assert state["step"] == 1
    assert (0, 0) in state["explored_cells"]


def test_finds_word_during_playback():
    player = TracePlayer(SAMPLE_EVENTS)

    for _ in range(5):
        player.step_forward()

    state = player.get_state()

    assert "CAT" in state["found_words"]
    assert state["found_words"]["CAT"] == [
        (0, 0), (0, 1), (0, 2)
    ]


def test_step_backward():
    player = TracePlayer(SAMPLE_EVENTS)

    player.step_forward()
    player.step_forward()
    player.step_backward()

    assert player.get_state()["step"] == 1


def test_reset():
    player = TracePlayer(SAMPLE_EVENTS)

    player.step_forward()
    player.step_forward()
    player.reset()

    state = player.get_state()

    assert state["step"] == 0
    assert not state["explored_cells"]
    assert not state["matched_cells"]
    assert not state["found_words"]


def test_playback_stops_at_end():
    player = TracePlayer(SAMPLE_EVENTS)

    for _ in range(len(SAMPLE_EVENTS)):
        assert player.step_forward() is not None

    assert player.is_finished
    assert player.step_forward() is None


def test_backward_at_start():
    player = TracePlayer(SAMPLE_EVENTS)

    assert player.step_backward() is None
    assert player.get_state()["step"] == 0


def test_backtrack_marks_failed_cells():
    player = TracePlayer(SAMPLE_EVENTS)

    for _ in range(len(SAMPLE_EVENTS)):
        player.step_forward()

    assert (1, 0) in player.get_state()["failed_cells"]
