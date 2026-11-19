"""People stay signed in across a restart, and nothing on disk signs anyone in."""

import json
import shutil
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import FakeGithub
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace
from token_of import token_of

from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS
from tadu.workspace_file_names import SESSIONS_FILE


@pytest.fixture
def workspace(tmp_path: Path, clock: BoardClock) -> Path:
    assert clock.now
    (tmp_path / "workspace").mkdir()
    return team_workspace(tmp_path / "workspace")


def seen(board: BoardServer, cookie: str) -> list[str] | int:
    response = call(board, "GET", "/api/cards", cookie)
    if response.status != 200:
        return response.status
    body = json.loads(response.body)
    assert body["user"] in {"Ana-Dev", "bo"}
    return sorted(card["repository"] for card in body["cards"])


def test_people_stay_signed_in_across_restarts(workspace: Path, github: FakeGithub) -> None:
    with serve_team_board(workspace, github) as board:
        ana, bo = sign_in_as(board, "Ana-Dev"), sign_in_as(board, "bo")
        assert seen(board, ana) == ["shop", "vault"]
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, ana) == ["shop", "vault"]
        assert seen(restarted, bo) == ["shop"]
        assert b'src="app.js"' in call(restarted, "GET", "/", ana).body
        assert call(restarted, "POST", "/auth/logout", ana).status == 200
    with serve_team_board(workspace, github) as again:
        assert seen(again, ana) == 401
        assert seen(again, bo) == ["shop"]


def test_a_session_still_ends_unused_after_a_restart(
    workspace: Path, github: FakeGithub, clock: BoardClock
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
    clock.advance(IDLE_TIMEOUT_SECONDS - 1)
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, ana) == ["shop", "vault"]
    clock.advance(IDLE_TIMEOUT_SECONDS - 1)
    with serve_team_board(workspace, github) as again:
        assert seen(again, ana) == ["shop", "vault"]
    clock.advance(IDLE_TIMEOUT_SECONDS)
    with serve_team_board(workspace, github) as later:
        assert seen(later, ana) == 401


def test_a_token_renewed_before_a_restart_is_the_one_after_it(
    workspace: Path, github: FakeGithub, clock: BoardClock
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        clock.advance(github.token_seconds)
        assert seen(board, ana) == ["shop", "vault"]
    assert github.refreshes == 1
    clock.advance(github.token_seconds - 600)
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, ana) == ["shop", "vault"]
    assert github.refreshes == 1


def test_access_is_checked_again_after_a_restart(workspace: Path, github: FakeGithub) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        bo = sign_in_as(board, "bo")
        assert seen(board, ana) == ["shop", "vault"]
        github.revoke_app("bo")
    github.readable["Ana-Dev"].discard("acme/vault")
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, ana) == ["shop"]
        assert seen(restarted, bo) == 401
    with serve_team_board(workspace, github) as again:
        assert seen(again, bo) == 401


def test_deleting_the_file_while_stopped_signs_everyone_out(
    workspace: Path, github: FakeGithub
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
    (workspace / SESSIONS_FILE).unlink()
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, ana) == 401
        assert b'href="auth/login"' in call(restarted, "GET", "/", ana).body


def test_a_copy_of_the_file_signs_nobody_in(
    workspace: Path, github: FakeGithub, tmp_path: Path, clock: BoardClock
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        token = token_of(board, ana, clock.now)
    saved = (workspace / SESSIONS_FILE).read_text()
    assert token not in saved
    assert ana.partition("=")[2] not in saved
    (row_id,) = json.loads(saved)["sessions"]
    (tmp_path / "elsewhere").mkdir()
    elsewhere = team_workspace(tmp_path / "elsewhere")
    shutil.copy(workspace / SESSIONS_FILE, elsewhere / SESSIONS_FILE)
    with serve_team_board(elsewhere, github) as other:
        for guess in (row_id, row_id[:43], "x"):
            assert seen(other, f"tadu_session={guess}") == 401
        # The cookie, which only Ana's browser holds, is what opens her session.
        assert seen(other, ana) == ["shop", "vault"]


def test_an_unreadable_sessions_file_only_signs_everyone_out(
    workspace: Path, github: FakeGithub
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
    (workspace / SESSIONS_FILE).write_text("{garbage")
    with serve_team_board(workspace, github) as restarted:
        assert restarted.state.github is not None
        assert restarted.state.github.sessions.problem is not None
        assert seen(restarted, ana) == 401
        bo = sign_in_as(restarted, "bo")
    with serve_team_board(workspace, github) as again:
        assert seen(again, bo) == ["shop"]
