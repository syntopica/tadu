from tadu.state_names import STATE_NAMES
from tadu.task_states import TASK_STATE_MARKERS


def test_each_marker_names_its_task_state() -> None:
    assert {marker: name for name, marker in TASK_STATE_MARKERS.items()} == STATE_NAMES
