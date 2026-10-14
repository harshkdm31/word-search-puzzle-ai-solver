import streamlit.components.v1 as components
import os

_component = components.declare_component(
    "interactive_grid",
    path=os.path.dirname(os.path.abspath(__file__)),
)


def interactive_grid(grid, found_paths=None, key=None):
    return _component(
        grid=grid,
        found_paths=found_paths or [],
        key=key,
        default=[],
    )