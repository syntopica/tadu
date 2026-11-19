"""`--idle-timeout`: how long a GitHub session lasts without use, 14 days by default."""

import argparse
import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import fake_github
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

from tadu.idle_timeout import idle_timeout
from tadu.session_store import SessionStore
from tadu.token_grant import TokenGrant

HALF_HOUR = 1800


@pytest.mark.parametrize(
    ("text", "seconds"),
    [
        ("14d", 14 * 86400),
        ("8h", 8 * 3600),
        ("30m", 1800),
        (" 10M ", 600),
        ("1d12h", 36 * 3600),
        ("1h30m", 5400),
        ("365d", 365 * 86400),
    ],
)
def test_durations_in_days_hours_and_minutes(text: str, seconds: int) -> None:
    assert idle_timeout(text) == seconds


@pytest.mark.parametrize(
    "text", ["", "9m", "0d", "14", "2w", "366d", "1h1d", "-5m", "1.5h", "d", "8 h"]
)
def test_anything_else_is_refused(text: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="must be a duration from 10m to 365d"):
        idle_timeout(text)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def board(tmp_path: Path, clock: BoardClock) -> Iterator[BoardServer]:
    del clock  # the board's sessions start on the test's clock
    with (
        fake_github({"Ana-Dev": {"acme/shop"}}) as github,
        serve_team_board(team_workspace(tmp_path), github, idle_timeout=HALF_HOUR) as server,
    ):
        yield server


def test_a_short_session_ends_after_its_time_unused(board: BoardServer, clock: BoardClock) -> None:
    start = call(board, "GET", "/auth/login")
    state = cookies(start)["tadu_oauth_state"]
    back = call(
        board,
        "GET",
        f"/auth/callback?code=code-Ana-Dev&state={state_part(state)}",
        f"tadu_oauth_state={state}",
    )
    assert f"Max-Age={HALF_HOUR};" in back.headers.get_all("Set-Cookie", [])[0]
    ana = "tadu_session=" + cookies(back)["tadu_session"]
    answer = json.loads(call(board, "GET", "/api/session", ana).body)
    assert (answer["remaining"], answer["warn"]) == (HALF_HOUR, 300)
    clock.advance(HALF_HOUR - 1)
    assert call(board, "GET", "/api/session", ana).status == 200
    clock.advance(1)
    assert call(board, "GET", "/api/session", ana).status == 401


def test_use_pushes_the_end_back_every_tenth_of_it(board: BoardServer, clock: BoardClock) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    clock.advance(HALF_HOUR // 10 - 1)
    assert "Set-Cookie" not in call(board, "GET", "/api/cards", ana).headers
    clock.advance(1)
    kept = call(board, "GET", "/api/cards", ana)
    assert f"Max-Age={HALF_HOUR};" in kept.headers["Set-Cookie"]
    clock.advance(HALF_HOUR - 1)  # 33 minutes after signing in, 29:59 after the last use
    assert call(board, "GET", "/api/session", ana).status == 200
    clock.advance(1)
    assert call(board, "GET", "/api/cards", ana).status == 401


GRANT = TokenGrant("tok", None, None)


def test_a_shortened_timeout_ends_saved_sessions_with_longer_to_last(
    tmp_path: Path, clock: BoardClock
) -> None:
    path = tmp_path / "sessions.json"
    long = SessionStore(path).create("ana", GRANT, clock.now)  # 14 days to last
    clock.advance(14 * 86400 - 600)  # 10 minutes left
    short = SessionStore(path).create("bo", GRANT, clock.now - 14 * 86400 + 1200)  # 20 left
    restarted = SessionStore(path, idle_timeout=HALF_HOUR)
    assert restarted.find(long, clock.now) is not None  # 10 minutes left: within
    assert restarted.find(short, clock.now) is not None
    assert restarted.shortened == 0
    fresh = SessionStore(path).create("cy", GRANT, clock.now)  # 14 days to last
    again = SessionStore(path, idle_timeout=HALF_HOUR)
    assert again.find(fresh, clock.now) is None
    assert again.shortened == 1


def test_activity_on_an_open_page_pushes_the_end_back(
    board: BoardServer, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    clock.advance(HALF_HOUR // 10 - 1)
    early = call(board, "POST", "/api/session", ana)
    assert (early.status, "Set-Cookie" in early.headers) == (200, False)  # not due yet
    clock.advance(1)
    active = call(board, "POST", "/api/session", ana)
    assert f"Max-Age={HALF_HOUR};" in active.headers["Set-Cookie"]
    assert json.loads(active.body)["remaining"] == HALF_HOUR
    for _ in range(3):  # an hour and a half of activity, no page load
        clock.advance(HALF_HOUR - 60)
        assert call(board, "POST", "/api/session", ana).status == 200
    clock.advance(HALF_HOUR - 60)
    assert call(board, "GET", "/api/session", ana).status == 200  # a plain check...
    clock.advance(60)
    assert call(board, "GET", "/api/session", ana).status == 401  # ...is not activity


def test_only_sign_out_and_activity_are_posts(board: BoardServer) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert call(board, "POST", "/api/session").status == 401
    for path in ("/api/cards", "/", "/auth/login", "/api/sessions"):
        assert call(board, "POST", path, ana).status == 405, path


def test_a_board_in_a_subfolder_takes_activity_on_both_paths(tmp_path: Path) -> None:
    with (
        fake_github({"Ana-Dev": {"acme/shop"}}) as github,
        serve_team_board(team_workspace(tmp_path), github, "https://example.com/tadu") as board,
    ):
        ana = sign_in_as(board, "Ana-Dev", "/tadu")
        assert call(board, "POST", "/tadu/api/session", ana).status == 200
        assert call(board, "POST", "/api/session", ana).status == 200
