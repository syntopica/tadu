import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from board_server import post
from fake_github import FakeGithub, fake_github
from team_board import serve_team_board, sign_in_as
from team_workspace import team_workspace


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github({"Ana-Dev": {"acme/shop"}}) as fake:
        yield fake


def test_the_call_runs_over_the_repositories_the_login_reads(
    tmp_path: Path, github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        response = post(board, "/api/op/list", b"{}", Cookie=ana, **{"X-Tadu-Token": ""})
    output = json.loads(response.body)["output"]
    assert "shop item." in output
    assert "vault" not in output


def test_a_workspace_that_does_not_load_names_nothing(tmp_path: Path, github: FakeGithub) -> None:
    workspace = team_workspace(tmp_path)
    with serve_team_board(workspace, github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        (workspace / "tadu-workspace.toml").write_text(
            'version = 1\n[[project]]\nkey = "/secret"\nrepositories = ["ghost"]\n'
        )
        response = post(board, "/api/op/list", b"{}", Cookie=ana, **{"X-Tadu-Token": ""})
    assert response.status == 500
    assert b"ghost" not in response.body
    assert b"/secret" not in response.body
