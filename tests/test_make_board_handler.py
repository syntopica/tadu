from pathlib import Path

from board_states import board_state

from tadu.board_handler import BoardHandler
from tadu.board_state import BoardState
from tadu.cli import main
from tadu.github_sign_in import GithubSignIn
from tadu.make_board_handler import make_board_handler
from tadu.team_board_handler import TeamBoardHandler


def test_each_state_gets_its_own_class() -> None:
    first = board_state(Path("/a"))
    second = board_state(Path("/b"))
    bound, other = make_board_handler(first), make_board_handler(second)
    assert issubclass(bound, BoardHandler)
    assert bound.state is first
    assert other.state is second  # type: ignore[attr-defined]


def test_a_github_state_gets_the_team_handler() -> None:
    sign_in = GithubSignIn("id", "secret", "https://board.example.com")
    state = BoardState(Path("/a"), 14, "a", frozenset(), "read", main, sign_in)
    bound = make_board_handler(state)
    assert issubclass(bound, TeamBoardHandler)
    assert bound.state is state
    assert bound.sign_in is sign_in
    assert not issubclass(
        make_board_handler(BoardState(Path("/a"), 14, "a", frozenset(), "read", main)),
        TeamBoardHandler,
    )
