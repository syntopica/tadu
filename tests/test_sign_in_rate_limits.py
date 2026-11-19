"""A board that signs in with GitHub lets each address start and finish a sign-in only
so often, answering 429 with Retry-After beyond it.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from response import Response
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.board_headers import BOARD_HEADERS
from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_limiter import SignInLimiter


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"ana": {"acme/shop"}}) as fake:
        yield fake


def get(board: BoardServer, path: str, forwarded: str | None = None) -> Response:
    headers = {"Host": board.host} | ({"X-Forwarded-For": forwarded} if forwarded else {})
    return board.request("GET", path, headers)


def statuses(board: BoardServer, path: str, times: int, forwarded: str | None = None) -> list[int]:
    return [get(board, path, forwarded).status for _ in range(times)]


def test_ten_a_minute_by_default_then_429_with_retry_after(
    tmp_path: Path, github: FakeGithub, clock: BoardClock
) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        assert statuses(board, "/auth/login", 10) == [302] * 10
        refused = get(board, "/auth/login")
        assert refused.status == 429
        assert refused.headers["Retry-After"] == "60"
        assert refused.headers["Content-Type"] == "text/plain; charset=utf-8"
        assert refused.body.startswith(
            b"Too many sign-in attempts from your address. Try again in 60 seconds."
        )
        assert "Location" not in refused.headers
        assert "Set-Cookie" not in refused.headers
        for name, value in BOARD_HEADERS.items():
            assert refused.headers[name] == value
        clock.advance(60.5)
        assert get(board, "/auth/login").status == 302


def test_the_callback_has_its_own_limit_and_asks_github_nothing_beyond_it(
    tmp_path: Path, github: FakeGithub, clock: BoardClock
) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        assert statuses(board, "/auth/login", 10) == [302] * 10
        answers = statuses(board, "/auth/callback?code=code-x&state=s", 12)
        assert answers == [400] * 10 + [429] * 2
        assert get(board, "/auth/callback?code=code-ana&state=s").status == 429
        assert [r for r in github.requests if r.startswith("POST")] == []
        assert clock.now


def test_everything_else_is_not_limited(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        ana = sign_in_as(board, "ana")
        beyond = 12  # more than the default limit of 10
        for path in ("/", "/app.js", "/api/cards"):
            assert {call(board, "GET", path, ana).status for _ in range(beyond)} == {200}
        assert {call(board, "POST", "/auth/logout").status for _ in range(beyond)} == {200}


def test_each_address_behind_a_trusted_proxy_has_its_own_limit(
    tmp_path: Path, github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), github, proxy_hops=1) as board:
        assert statuses(board, "/auth/login", 11, "203.0.113.7") == [302] * 10 + [429]
        assert statuses(board, "/auth/login", 10, "198.51.100.1") == [302] * 10
        assert statuses(board, "/auth/login", 1, "1.2.3.4, 203.0.113.7") == [429]


def test_without_a_trusted_proxy_a_forged_header_changes_nothing(
    tmp_path: Path, github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        forged = [get(board, "/auth/login", f"203.0.113.{n}").status for n in range(12)]
        assert forged == [302] * 10 + [429] * 2


def test_a_limit_of_its_own_and_off(tmp_path: Path, github: FakeGithub, clock: BoardClock) -> None:
    strict = SignInLimiter(sign_in_limit("3/minute;5/hour"))
    with serve_team_board(team_workspace(tmp_path), github, limiter=strict) as board:
        assert statuses(board, "/auth/login", 4) == [302] * 3 + [429]
        clock.advance(60.5)
        assert statuses(board, "/auth/login", 3) == [302] * 2 + [429]
        assert get(board, "/auth/login").headers["Retry-After"] == str(3600 - 60)
    (tmp_path / "again").mkdir()
    off = SignInLimiter(sign_in_limit("off"))
    with serve_team_board(team_workspace(tmp_path / "again"), github, limiter=off) as board:
        assert set(statuses(board, "/auth/login", 40)) == {302}


def test_a_real_sign_in_fits_many_times_over(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        for _ in range(5):
            assert call(board, "GET", "/api/cards", sign_in_as(board, "ana")).status == 200
