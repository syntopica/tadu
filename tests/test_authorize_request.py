from dataclasses import replace
from pathlib import Path

from board_states import board_state

from tadu.authorize_request import authorize_request

STATE = replace(board_state(Path("/w"), hosts=frozenset({"127.0.0.1:1"})), token="secret")  # noqa: S106
HOST = "127.0.0.1:1"


def test_allowed() -> None:
    assert authorize_request(HOST, "secret", "/api/cards", STATE) is None


def test_host_checked_first_on_every_path() -> None:
    assert authorize_request("evil.example:1", "secret", "/", STATE) == 421
    assert authorize_request("evil.example:1", None, "/api/cards", STATE) == 421
    assert authorize_request(None, "secret", "/board.js", STATE) == 421


def test_assets_and_unknown_paths_need_no_token() -> None:
    for route in ("/", "/board.js", "/board.css", "/nope"):
        assert authorize_request(HOST, None, route, STATE) is None


def test_wrong_or_missing_token_on_data() -> None:
    assert authorize_request(HOST, "secreT", "/api/cards", STATE) == 403
    assert authorize_request(HOST, None, "/api/cards", STATE) == 403


def test_non_ascii_token_is_refused_not_raised() -> None:
    assert authorize_request(HOST, "sécret", "/api/cards", STATE) == 403


def test_only_the_cards_need_the_token() -> None:
    for route in ("/api/history", "/api/changes", "/api/op/list"):
        assert authorize_request(HOST, None, route, STATE) is None
