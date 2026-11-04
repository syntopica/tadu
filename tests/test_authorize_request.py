from pathlib import Path

from tadu.authorize_request import authorize_request
from tadu.board_state import BoardState

STATE = BoardState(Path("/w"), 14, "secret", frozenset({"127.0.0.1:1"}))


def test_allowed() -> None:
    assert authorize_request("127.0.0.1:1", "secret", STATE) is None


def test_host_checked_before_token() -> None:
    assert authorize_request("evil.example:1", None, STATE) == 421
    assert authorize_request(None, "secret", STATE) == 421


def test_wrong_or_missing_token() -> None:
    assert authorize_request("127.0.0.1:1", "secreT", STATE) == 403
    assert authorize_request("127.0.0.1:1", None, STATE) == 403


def test_non_ascii_token_is_refused_not_raised() -> None:
    assert authorize_request("127.0.0.1:1", "sécret", STATE) == 403
