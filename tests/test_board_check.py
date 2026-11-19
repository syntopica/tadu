"""`api/session`: an open page asks, lightly, whether it may still show what it shows."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer, get, send, serve_board
from board_workspace import board_workspace
from fake_github import FakeGithub, fake_github
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS

DAY = 24 * 3600
EARLIER_TOKEN = "earlier-run"  # noqa: S105 - a token of a run that ended


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}}) as fake:
        yield fake


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def team(tmp_path: Path, github: FakeGithub) -> Iterator[BoardServer]:
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def test_a_token_board_checks_the_token(tmp_path: Path, capfd: pytest.CaptureFixture[str]) -> None:
    with serve_board(board_workspace(tmp_path)) as board:
        passed = get(board, "/api/session", host=board.host, token=board.token)
        assert (passed.status, json.loads(passed.body)) == (200, {"ok": True})
        assert get(board, "/api/session", host=board.host, token=None).status == 403
        assert get(board, "/api/session", host=board.host, token=EARLIER_TOKEN).status == 403
        assert get(board, "/api/session", host="evil.example", token=board.token).status == 421
    # Every open page checks twice a minute: only failed checks are logged.
    assert capfd.readouterr().err.splitlines() == [
        "GET /api/session 403",
        "GET /api/session 403",
        "GET /api/session 421",
    ]


def test_a_team_board_checks_the_session(
    team: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(team, "Ana-Dev")
    asked = len(github.requests)
    passed = call(team, "GET", "/api/session", ana)
    # The seconds the session has left unused, and how long before the end the page warns.
    assert (passed.status, json.loads(passed.body)) == (
        200,
        {"ok": True, "remaining": IDLE_TIMEOUT_SECONDS, "warn": 300},
    )
    clock.advance(3600)
    assert json.loads(call(team, "GET", "/api/session", ana).body)["remaining"] == (
        IDLE_TIMEOUT_SECONDS - 3600
    )
    assert "Set-Cookie" not in passed.headers
    assert len(github.requests) == asked  # GitHub is not asked
    for cookie in ("", "tadu_session=forged"):
        refused = call(team, "GET", "/api/session", cookie)
        assert (refused.status, json.loads(refused.body)) == (401, {"error": "signed out"})
        assert refused.headers["Set-Cookie"].startswith("tadu_session=; Path=/; Max-Age=0")
    assert call(team, "POST", "/auth/logout", ana).status == 200
    assert call(team, "GET", "/api/session", ana).status == 401


def test_checking_does_not_keep_a_session_alive(team: BoardServer, clock: BoardClock) -> None:
    ana = sign_in_as(team, "Ana-Dev")
    for _ in range(IDLE_TIMEOUT_SECONDS // DAY - 1):
        clock.advance(DAY)
        assert call(team, "GET", "/api/session", ana).status == 200
    clock.advance(2 * DAY)  # 15 days after the last use: the checks did not count
    assert call(team, "GET", "/api/session", ana).status == 401
    assert call(team, "GET", "/api/cards", ana).status == 401


def test_a_board_in_a_subfolder_answers_both_paths(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github, "https://example.com/tadu") as board:
        ana = sign_in_as(board, "Ana-Dev", "/tadu")
        assert call(board, "GET", "/tadu/api/session", ana).status == 200
        assert call(board, "GET", "/api/session", ana).status == 200
        refused = call(board, "GET", "/tadu/api/session")
        assert refused.status == 401
        assert refused.headers["Set-Cookie"].startswith("__Secure-tadu_session=; Path=/tadu/;")


def test_a_token_board_takes_no_post(tmp_path: Path) -> None:
    with serve_board(board_workspace(tmp_path)) as board:
        assert send(board, "POST", "/api/session").status == 405
