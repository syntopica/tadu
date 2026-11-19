"""Access that changes on GitHub while people are signed in, and repositories that move."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import FakeGithub
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.sign_in_settings import ACCESS_SECONDS, RETRY_SECONDS

REPLACED = (
    "a repository is hidden because the board cannot confirm it is still the same "
    "repository on GitHub; the board's operator has been told which"
)


@pytest.fixture
def board(tmp_path: Path, github: FakeGithub, clock: BoardClock) -> Iterator[BoardServer]:
    assert clock.now
    with serve_team_board(team_workspace(tmp_path), github) as server:
        yield server


def seen(board: BoardServer, cookie: str) -> list[str]:
    response = call(board, "GET", "/api/cards", cookie)
    assert response.status == 200, response.body
    return sorted(card["repository"] for card in json.loads(response.body)["cards"])


def problems(board: BoardServer, cookie: str) -> list[str]:
    body = json.loads(call(board, "GET", "/api/cards", cookie).body)
    return [p["message"] for p in body["problems"]]


def test_removed_from_the_team_mid_session(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert seen(board, ana) == ["shop", "vault"]
    github.readable["Ana-Dev"].discard("acme/vault")
    clock.advance(ACCESS_SECONDS - 1)
    assert seen(board, ana) == ["shop", "vault"]
    clock.advance(1)
    assert seen(board, ana) == ["shop"]
    assert call(board, "GET", "/", ana).status == 200


def test_a_public_repository_made_private_mid_session(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    github.public.add("acme/vault")
    bo = sign_in_as(board, "bo")
    assert seen(board, bo) == ["shop", "vault"]
    github.public.clear()
    clock.advance(ACCESS_SECONDS)
    assert seen(board, bo) == ["shop"]


def test_a_repository_deleted_mid_session(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    github.readable["Ana-Dev"].discard("acme/shop")
    github.readable["bo"].clear()
    clock.advance(ACCESS_SECONDS)
    assert seen(board, ana) == ["vault"]


def test_a_token_that_expires_mid_session_is_renewed(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert seen(board, ana) == ["shop", "vault"]
    clock.advance(github.token_seconds)
    assert seen(board, ana) == ["shop", "vault"]
    assert github.refreshes == 1


def test_the_app_revoked_mid_session_ends_it(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert seen(board, ana) == ["shop", "vault"]
    github.revoke_app("Ana-Dev")
    clock.advance(ACCESS_SECONDS)
    assert call(board, "GET", "/api/cards", ana).status == 401
    assert b'href="auth/login"' in call(board, "GET", "/", ana).body


def test_saml_enforced_mid_session_hides_and_says_so(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    github.public.add("acme/vault")
    bo = sign_in_as(board, "bo")
    assert seen(board, bo) == ["shop", "vault"]
    github.sso.add("acme/vault")
    clock.advance(ACCESS_SECONDS)
    assert seen(board, bo) == ["shop"]
    assert problems(board, bo) == [
        "GitHub answered HTTP 403, so some repositories are hidden until Reload can check them"
    ]
    asked = len(github.requests)
    clock.advance(RETRY_SECONDS - 1)
    seen(board, bo)
    assert len(github.requests) == asked


def test_a_renamed_repository_keeps_showing_and_the_operator_is_told(
    board: BoardServer, github: FakeGithub, clock: BoardClock, capfd: pytest.CaptureFixture[str]
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    seen(board, ana)
    github.renamed["acme/vault"] = "acme/vault-v2"
    github.repo_ids["acme/vault-v2"] = github.repo_id("acme/vault")
    github.readable["Ana-Dev"] = {"acme/shop", "acme/vault-v2"}
    for _ in range(2):
        clock.advance(ACCESS_SECONDS)
        assert seen(board, ana) == ["shop", "vault"]
        assert problems(board, ana) == []
    warning = (
        "tadu board: warning: acme/vault is now acme/vault-v2 on GitHub; "
        "update the remote of its workspace repository\n"
    )
    assert capfd.readouterr().err.count(warning) == 1


def test_a_transferred_repository_is_followed_too(
    board: BoardServer, github: FakeGithub, clock: BoardClock
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    seen(board, ana)
    github.renamed["acme/vault"] = "newco/vault"
    github.repo_ids["newco/vault"] = github.repo_id("acme/vault")
    github.readable["Ana-Dev"] = {"acme/shop", "newco/vault"}
    clock.advance(ACCESS_SECONDS)
    assert seen(board, ana) == ["shop", "vault"]


def test_a_new_repository_under_an_old_name_shows_to_nobody(
    board: BoardServer, github: FakeGithub, clock: BoardClock, capfd: pytest.CaptureFixture[str]
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert seen(board, ana) == ["shop", "vault"]
    github.readable["Ana-Dev"] = {"acme/shop", "acme/vault-v2"}
    github.repo_ids["acme/vault-v2"] = github.repo_id("acme/vault")
    github.repo_ids["acme/vault"] = 999
    github.public.add("acme/vault")
    bo = sign_in_as(board, "bo")
    assert seen(board, bo) == ["shop"]
    assert problems(board, bo) == [REPLACED]
    clock.advance(ACCESS_SECONDS)
    assert seen(board, ana) == ["shop"]
    original = github.repo_id("acme/vault-v2")
    assert (
        "tadu board: warning: repository vault: acme/vault on GitHub is repository id 999, "
        f"not {original} (the id first seen); it is hidden from everyone. If acme/vault is the "
        "right repository, set github_id = 999 on it in tadu-workspace.toml\n"
    ) in capfd.readouterr().err


def test_a_login_given_up_and_taken_by_someone_else_inherits_nothing(
    board: BoardServer, github: FakeGithub
) -> None:
    ana = sign_in_as(board, "Ana-Dev")
    assert seen(board, ana) == ["shop", "vault"]
    github.readable["Ana-Dev"] = set()
    github.user_ids["Ana-Dev"] = 424242
    newcomer = sign_in_as(board, "Ana-Dev")
    assert seen(board, newcomer) == []
    assert seen(board, ana) == ["shop", "vault"]


def test_people_never_see_each_others_answers(board: BoardServer) -> None:
    ana, bo = sign_in_as(board, "Ana-Dev"), sign_in_as(board, "bo")
    assert seen(board, ana) == ["shop", "vault"]
    assert seen(board, bo) == ["shop"]
    assert seen(board, ana) == ["shop", "vault"]
