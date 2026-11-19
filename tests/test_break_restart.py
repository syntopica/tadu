"""A repository's GitHub identity survives restarts, so a taken-over name never shows."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_clock import BoardClock
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from team_board import call, serve_team_board, sign_in_as
from team_workspace import team_workspace

from tadu.sign_in_settings import ACCESS_SECONDS
from tadu.workspace_file_names import GITHUB_IDS_FILE

UNCONFIRMED = (
    "a repository is hidden because the board cannot confirm it is still the same "
    "repository on GitHub; the board's operator has been told which"
)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop", "acme/vault"}, "bo": {"acme/shop"}}) as fake:
        yield fake


@pytest.fixture
def workspace(tmp_path: Path, clock: BoardClock) -> Path:
    assert clock.now
    return team_workspace(tmp_path)


def seen(board: BoardServer, cookie: str) -> tuple[list[str], list[str]]:
    response = call(board, "GET", "/api/cards", cookie)
    assert response.status == 200, response.body
    body = json.loads(response.body)
    return sorted(c["repository"] for c in body["cards"]), [p["message"] for p in body["problems"]]


def take_over_vault(github: FakeGithub) -> None:
    """acme/vault is renamed to acme/vault-v2, then someone creates a public acme/vault."""
    github.repo_ids["acme/vault-v2"] = github.repo_id("acme/vault")
    github.readable["Ana-Dev"] = {"acme/shop", "acme/vault-v2"}
    github.repo_ids["acme/vault"] = 999
    github.public.add("acme/vault")


def set_github_id(workspace: Path, key: str, repository_id: int) -> None:
    toml = workspace / "tadu-workspace.toml"
    line = f'[[repository]]\nkey = "{key}"\n'
    toml.write_text(toml.read_text().replace(line, f"{line}github_id = {repository_id}\n"))


def test_a_takeover_after_a_restart_still_shows_to_nobody(
    workspace: Path, github: FakeGithub, capfd: pytest.CaptureFixture[str]
) -> None:
    with serve_team_board(workspace, github) as board:
        assert seen(board, sign_in_as(board, "Ana-Dev"))[0] == ["shop", "vault"]
    take_over_vault(github)
    with serve_team_board(workspace, github) as restarted:
        assert seen(restarted, sign_in_as(restarted, "bo")) == (["shop"], [UNCONFIRMED])
        assert seen(restarted, sign_in_as(restarted, "Ana-Dev")) == (["shop"], [UNCONFIRMED])
    assert "repository vault: acme/vault on GitHub is repository id 999" in capfd.readouterr().err


def test_the_learned_ids_are_written_beside_the_workspace_once(
    workspace: Path, github: FakeGithub, clock: BoardClock
) -> None:
    ids = workspace / GITHUB_IDS_FILE
    with serve_team_board(workspace, github) as board:
        bo = sign_in_as(board, "bo")
        seen(board, bo)
        assert json.loads(ids.read_text()) == {
            "version": 1,
            "github_ids": {"shop": github.repo_id("acme/shop")},
        }
        ana = sign_in_as(board, "Ana-Dev")
        seen(board, ana)
        written = ids.read_text()
        assert list(json.loads(written)["github_ids"]) == ["shop", "vault"]
        clock.advance(ACCESS_SECONDS)
        seen(board, ana)
        seen(board, bo)
        assert ids.read_text() == written


def test_github_id_protects_a_board_that_never_saw_the_repository(
    workspace: Path, github: FakeGithub
) -> None:
    original = github.repo_id("acme/vault")
    take_over_vault(github)
    set_github_id(workspace, "vault", original)
    with serve_team_board(workspace, github) as board:
        assert seen(board, sign_in_as(board, "bo")) == (["shop"], [UNCONFIRMED])
    assert "vault" not in json.loads((workspace / GITHUB_IDS_FILE).read_text())["github_ids"]


def test_github_id_that_matches_shows_the_repository(workspace: Path, github: FakeGithub) -> None:
    set_github_id(workspace, "vault", github.repo_id("acme/vault"))
    with serve_team_board(workspace, github) as board:
        assert seen(board, sign_in_as(board, "Ana-Dev")) == (["shop", "vault"], [])


def test_the_operator_confirms_a_deliberate_change_without_a_restart(
    workspace: Path, github: FakeGithub, clock: BoardClock
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        seen(board, ana)
        github.repo_ids["acme/vault"] = 777
        clock.advance(ACCESS_SECONDS)
        assert seen(board, ana) == (["shop"], [UNCONFIRMED])
        set_github_id(workspace, "vault", 777)
        assert seen(board, ana) == (["shop", "vault"], [])


def test_a_remote_pointed_at_another_repository_is_caught(
    workspace: Path, github: FakeGithub, clock: BoardClock, capfd: pytest.CaptureFixture[str]
) -> None:
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        seen(board, ana)
        toml = workspace / "tadu-workspace.toml"
        toml.write_text(toml.read_text().replace("acme/shop", "acme/vault"))
        clock.advance(ACCESS_SECONDS)
        assert seen(board, ana) == (["vault"], [UNCONFIRMED])
    assert "repository shop: acme/vault on GitHub is repository id" in capfd.readouterr().err


def test_ids_that_cannot_be_written_down_are_not_trusted(
    workspace: Path, github: FakeGithub, capfd: pytest.CaptureFixture[str]
) -> None:
    with serve_team_board(workspace, github) as board:
        (workspace / GITHUB_IDS_FILE).mkdir()
        bo = sign_in_as(board, "bo")
        assert seen(board, bo) == ([], [UNCONFIRMED])
        set_github_id(workspace, "shop", github.repo_id("acme/shop"))
        assert seen(board, bo) == (["shop"], [])
    err = capfd.readouterr().err
    assert f"repository shop: cannot record its GitHub id in {GITHUB_IDS_FILE}" in err
    assert f"until github_id = {github.repo_id('acme/shop')} is set on it" in err
