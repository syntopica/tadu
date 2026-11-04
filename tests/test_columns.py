from tadu.columns import COLUMNS


def test_columns_in_board_order() -> None:
    assert COLUMNS == ("backlog", "ready", "in_progress", "blocked", "done", "cancelled")
