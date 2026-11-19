"""Sessions of a board that signs in with GitHub: signing in again, ending, failing."""

import json
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS, KEEP_ALIVE_SECONDS


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop", "acme/vault"}}) as fake:
        yield fake


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub) -> Iterator[BoardServer]:
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def test_signing_in_again_ends_the_session_the_browser_held(board: BoardServer) -> None:
    old = sign_in_as(board, "Ana-Dev")
    start = call(board, "GET", "/auth/login")
    state = cookies(start)["tadu_oauth_state"]
    back = call(
        board,
        "GET",
        f"/auth/callback?code=code-Ana-Dev~again&state={state_part(state)}",
        f"tadu_oauth_state={state}; {old}",
    )
    new = f"tadu_session={cookies(back)['tadu_session']}"
    assert call(board, "GET", "/api/cards", old).status == 401
    assert call(board, "GET", "/api/cards", new).status == 200


def test_a_refused_token_leaves_nothing_behind(board: BoardServer, github: FakeGithub) -> None:
    assert board.state.github is not None
    sign_in = board.state.github
    cookie = sign_in_as(board, "Ana-Dev")
    assert call(board, "GET", "/api/cards", cookie).status == 200
    session = sign_in.sessions.find(cookie.partition("=")[2], time.time())
    assert session is not None
    known = sign_in.access.for_session(session.id, time.time())
    assert known.listed
    github.revoke_app("Ana-Dev")
    known.listed_at = float("-inf")
    assert call(board, "GET", "/api/cards", cookie).status == 401
    assert sign_in.access.for_session(session.id, time.time()) is not known


def test_a_workspace_that_breaks_names_nothing_to_the_page(
    board: BoardServer, capfd: pytest.CaptureFixture[str]
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    toml = board.state.workspace / "tadu-workspace.toml"
    toml.write_text(toml.read_text() + '[[repository]]\nkey = "vault"\n')
    broken = call(board, "GET", "/api/cards", ana)
    assert broken.status == 500
    assert json.loads(broken.body) == {
        "error": "the workspace does not load; the board's operator can see why"
    }
    assert b"vault" not in broken.body
    assert "tadu board: duplicate repository key: vault" in capfd.readouterr().err


def test_a_token_endpoint_down_at_renewal_signs_nobody_out(
    board: BoardServer, github: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = BoardClock(monkeypatch)
    ana = sign_in_as(board, "Ana-Dev")
    assert len(json.loads(call(board, "GET", "/api/cards", ana).body)["cards"]) == 2
    github.token_endpoint_down = True
    clock.advance(github.token_seconds)
    down = call(board, "GET", "/api/cards", ana)
    assert down.status == 200
    body = json.loads(down.body)
    assert body["cards"] == []
    assert [p["message"] for p in body["problems"]] == [
        "GitHub could not be reached, so some repositories are hidden until Reload can check them"
    ]
    github.token_endpoint_down = False
    back = json.loads(call(board, "GET", "/api/cards", ana).body)
    assert (len(back["cards"]), back["problems"]) == (2, [])
    assert github.refreshes == 1


def test_a_used_session_is_kept_alive_once_a_day(
    board: BoardServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = BoardClock(monkeypatch)
    ana = sign_in_as(board, "Ana-Dev")
    assert "Set-Cookie" not in call(board, "GET", "/api/cards", ana).headers
    clock.advance(KEEP_ALIVE_SECONDS - 1)
    assert "Set-Cookie" not in call(board, "GET", "/api/cards", ana).headers
    clock.advance(1)
    kept = call(board, "GET", "/api/cards", ana)
    assert kept.headers["Set-Cookie"] == (
        f"{ana}; Path=/; Max-Age={IDLE_TIMEOUT_SECONDS}; HttpOnly; SameSite=Lax"
    )
    assert "Set-Cookie" not in call(board, "GET", "/api/cards", ana).headers
    clock.advance(IDLE_TIMEOUT_SECONDS - 1)
    assert call(board, "GET", "/api/cards", ana).status == 200
