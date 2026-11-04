from pathlib import Path

from tadu.board_handler import BoardHandler
from tadu.board_state import BoardState
from tadu.make_board_handler import make_board_handler


def test_each_state_gets_its_own_class() -> None:
    first = BoardState(Path("/a"), 14, "a", frozenset())
    second = BoardState(Path("/b"), 14, "b", frozenset())
    bound, other = make_board_handler(first), make_board_handler(second)
    assert issubclass(bound, BoardHandler)
    assert bound.state is first
    assert other.state is second  # type: ignore[attr-defined]
