"""A session cookie copied to another browser: what the thief keeps, and for how long."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer, Response
from fake_github import FakeGithub, fake_github
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.sign_in_settings import ACCESS_SECONDS, IDLE_TIMEOUT_SECONDS


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}}) as fake:
        yield fake


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub, clock: BoardClock) -> Iterator[BoardServer]:
    assert clock.now
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def cards(board: BoardServer, cookie: str) -> Response:
    return call(board, "GET", "/api/cards", cookie)


def token_of(board: BoardServer, cookie: str, now: float) -> str:
    assert board.state.github is not None
    session = board.state.github.sessions.find(cookie.partition("=")[2], now)
    assert session is not None
    assert session.token is not None
    return session.token


def test_the_victim_signing_out_ends_the_thiefs_copy(board: BoardServer) -> None:
    victim = sign_in_as(board, "Ana-Dev")
    thief = victim
    assert cards(board, thief).status == 200
    assert call(board, "POST", "/auth/logout", victim).status == 200
    assert cards(board, thief).status == 401
    assert b'href="auth/login"' in call(board, "GET", "/", thief).body


def test_a_stolen_cookie_dies_when_the_session_goes_unused(
    board: BoardServer, clock: BoardClock
) -> None:
    thief = sign_in_as(board, "Ana-Dev")
    clock.advance(IDLE_TIMEOUT_SECONDS - 1)
    assert cards(board, thief).status == 200
    clock.advance(IDLE_TIMEOUT_SECONDS - 1)
    assert cards(board, thief).status == 200
    clock.advance(IDLE_TIMEOUT_SECONDS)
    assert cards(board, thief).status == 401


def test_a_revoked_app_refuses_a_copy_that_has_not_loaded_yet(
    board: BoardServer, github: FakeGithub
) -> None:
    stolen = sign_in_as(board, "Ana-Dev")
    github.revoke_app("Ana-Dev")
    assert cards(board, stolen).status == 401


def test_revoking_the_app_on_github_ends_the_thiefs_copy_within_minutes(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    stolen = sign_in_as(board, "Ana-Dev")
    assert cards(board, stolen).status == 200
    github.revoke_app("Ana-Dev")
    fresh = sign_in_as(board, "Ana-Dev")
    for _ in range(ACCESS_SECONDS // 60 - 1):
        clock.advance(60)
        assert cards(board, fresh).status == 200
        assert cards(board, stolen).status == 200
    clock.advance(60)
    assert cards(board, fresh).status == 200
    assert cards(board, stolen).status == 401
    assert cards(board, stolen).status == 401
    assert cards(board, fresh).status == 200


@pytest.mark.parametrize(
    "forge",
    [
        lambda value: value[:-1] + ("A" if value[-1] != "A" else "B"),
        lambda value: value[:20],
        lambda value: value + "x",
        lambda value: value.upper(),
        lambda _value: "",
        lambda _value: "../../etc/passwd",
    ],
)
def test_a_tampered_cookie_is_nobody(board: BoardServer, forge: object) -> None:
    name, _, value = sign_in_as(board, "Ana-Dev").partition("=")
    forged = f"{name}={forge(value)}"  # type: ignore[operator]
    assert cards(board, forged).status == 401
    assert b'href="auth/login"' in call(board, "GET", "/", forged).body


def test_a_cookie_from_before_a_restart_is_nobody(
    tmp_path: Path, github: FakeGithub, board: BoardServer
) -> None:
    cookie = sign_in_as(board, "Ana-Dev")
    (tmp_path / "again").mkdir()
    with serve_team_board(team_workspace(tmp_path / "again"), github) as restarted:
        assert cards(restarted, cookie).status == 401


def test_no_response_carries_the_github_token(board: BoardServer, clock: BoardClock) -> None:
    cookie = sign_in_as(board, "Ana-Dev")
    token = token_of(board, cookie, clock.now)
    responses = [
        cards(board, cookie),
        call(board, "GET", "/", cookie),
        call(board, "GET", "/app.js", cookie),
        call(board, "POST", "/auth/logout", cookie),
        cards(board, cookie),
    ]
    for response in responses:
        assert token not in response.body.decode()
        assert all(token not in value for value in response.headers.values())
    payload = json.loads(responses[0].body)
    assert payload["user"] == "Ana-Dev"
