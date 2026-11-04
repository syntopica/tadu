from tadu.state_columns import STATE_COLUMNS


def test_every_non_open_state_has_a_column() -> None:
    assert STATE_COLUMNS == {"~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}
