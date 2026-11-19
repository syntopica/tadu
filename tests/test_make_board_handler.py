from pathlib import Path

from board_states import board_state

from tadu.board_handler import BoardHandler
from tadu.make_board_handler import make_board_handler


def test_each_state_gets_its_own_class() -> None:
    first = board_state(Path("/a"))
    second = board_state(Path("/b"))
    bound, other = make_board_handler(first), make_board_handler(second)
    assert issubclass(bound, BoardHandler)
    assert bound.state is first
    assert other.state is second  # type: ignore[attr-defined]
