"""Ending a session on purpose has GitHub revoke its token, so no copy of it still works."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from team_board import call, cookies, serve_team_board, sign_in_as, state_part
from team_workspace import team_workspace

from tadu.github_call import github_call
from tadu.revoke_github_token import revoke_github_token

REVOKE = "DELETE /api/applications/client-1/token"


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}}) as fake:
        yield fake


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub) -> Iterator[BoardServer]:
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def last_token(github: FakeGithub) -> str:
    return list(github.tokens)[-1]


def test_signing_out_revokes_the_token(board: BoardServer, github: FakeGithub) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    token = last_token(github)
    assert github_call(f"{github.url}/api/user", token).status == 200
    assert call(board, "POST", "/auth/logout", ana).status == 200
    assert REVOKE in github.requests
    assert github_call(f"{github.url}/api/user", token).status == 401  # dead at GitHub too


def test_signing_in_again_revokes_the_token_it_replaces(
    board: BoardServer, github: FakeGithub
) -> None:
    first = sign_in_as(board, "Ana-Dev")
    old = last_token(github)
    kept = cookies(call(board, "GET", "/auth/login"))["tadu_oauth_state"]
    back = call(
        board,
        "GET",
        f"/auth/callback?code=code-Ana-Dev~again&state={state_part(kept)}",
        f"tadu_oauth_state={kept}; {first}",  # the same browser, still signed in
    )
    assert back.status == 302
    assert old in github.revoked
    assert last_token(github) not in github.revoked
    assert call(board, "GET", "/api/session", first).status == 401


def test_a_github_down_does_not_stop_a_sign_out(board: BoardServer, github: FakeGithub) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    github.token_endpoint_down = True
    assert call(board, "POST", "/auth/logout", ana).status == 200
    assert call(board, "GET", "/api/session", ana).status == 401


def test_revoking_needs_the_apps_own_credentials(github: FakeGithub) -> None:
    sign_in = github.sign_in()
    assert revoke_github_token(sign_in, "tok-ana") is True
    assert "tok-ana" in github.revoked
    wrong = sign_in.__class__(
        "client-1", "wrong", sign_in.public_url, github.url, f"{github.url}/api"
    )
    assert revoke_github_token(wrong, "tok-bo") is False
    other = sign_in.__class__(
        "client-2", "shh", sign_in.public_url, github.url, f"{github.url}/api"
    )
    assert revoke_github_token(other, "tok-bo") is False
    unreachable = sign_in.__class__(
        "client-1", "shh", sign_in.public_url, api_url="http://127.0.0.1:9"
    )
    assert revoke_github_token(unreachable, "tok-bo") is False
    assert "tok-bo" not in github.revoked
