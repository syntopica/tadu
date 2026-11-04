import pytest

from tadu.item_column import item_column


@pytest.mark.parametrize(
    ("state", "queue", "column"),
    [
        (" ", "backlog", "backlog"),
        (" ", "ready", "ready"),
        ("~", "backlog", "in_progress"),
        ("!", "backlog", "blocked"),
        ("x", "backlog", "done"),
        ("-", "backlog", "cancelled"),
    ],
)
def test_item_column(state: str, queue: str, column: str) -> None:
    assert item_column(state, queue) == column
