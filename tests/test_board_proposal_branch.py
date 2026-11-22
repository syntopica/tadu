"""A repository's `branch` setting: proposals target it instead of the default branch."""

from pathlib import Path

import pytest
from fake_github import FakeGithub
from test_team_board_proposals import github, propose, signed_in

__all__ = ["github"]  # the fixture the tests below take

MARK: dict[str, object] = {"match": "shop item", "state": "blocked", "note": "waiting"}


def target_dev(workspace: Path, github: FakeGithub) -> None:
    """GitHub's default stays main, while the backlog lives on dev and the workspace says so."""
    github.git.default_branch = "main"
    file = workspace / "tadu-workspace.toml"
    shop = 'key = "shop"\n'
    file.write_text(file.read_text().replace(shop, f'{shop}branch = "dev"\n'))


@pytest.mark.parametrize("mode", ["direct", "pr"])
def test_a_change_lands_on_the_repository_branch(
    tmp_path: Path, github: FakeGithub, mode: str
) -> None:
    github.git.default_branch = "dev"  # seeded on dev only
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals=mode) as (workspace, board, ana):
        target_dev(workspace, github)
        seen = propose(board, ana, "mark", MARK)
    assert seen["code"] == 0, seen
    assert "heads/main" not in github.git.refs["acme/shop"]
    if mode == "direct":
        assert github.git.refs["acme/shop"]["heads/dev"] != "commit-acme/shop"
    else:
        (pull,) = [body for tail, _, _, body in github.git.created if tail == "pulls"]
        assert pull["base"] == "dev"
