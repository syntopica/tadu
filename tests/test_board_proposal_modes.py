import json
from pathlib import Path

import pytest
from fake_github import FakeGithub
from test_team_board_calls import operate
from test_team_board_proposals import github, propose, signed_in

__all__ = ["github"]  # the fixture the tests below take

MARK: dict[str, object] = {"match": "shop item", "state": "blocked", "note": "waiting"}


def test_merge_mode_opens_the_pull_request_and_merges_it(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals="merge") as (_, board, ana):
        seen = propose(board, ana, "mark", MARK)
    assert seen["code"] == 0, seen
    assert str(seen["output"]).startswith("merged: https://github.test/acme/shop/pull/")
    kinds = [tail for tail, *_ in github.git.created]
    assert kinds[-2] == "pulls"
    assert kinds[-1].startswith("PUT pulls/")
    (merge,) = [body for tail, _, _, body in github.git.created if tail.startswith("PUT ")]
    assert merge == {"merge_method": "squash"}


def test_merge_mode_leaves_the_pull_request_open_when_github_refuses_to_merge(
    tmp_path: Path, github: FakeGithub
) -> None:
    github.git.protected.add("acme/shop")
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals="merge") as (_, board, ana):
        seen = propose(board, ana, "mark", MARK)
    assert str(seen["output"]).startswith("proposed: https://github.test/acme/shop/pull/")
    assert "would not merge" in str(seen["output"])


def test_direct_mode_commits_to_the_default_branch_without_a_branch_or_pull_request(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals="direct") as (_, board, ana):
        seen = propose(board, ana, "mark", MARK)
    assert seen["code"] == 0, seen
    assert str(seen["output"]).startswith("committed: https://github.test/acme/shop/commit/commit-")
    assert [tail for tail, *_ in github.git.created] == [
        "git/trees",
        "git/commits",
        "PATCH git/refs/heads/main",
    ]
    (move,) = [body for tail, _, _, body in github.git.created if tail.startswith("PATCH ")]
    assert move["force"] is False
    assert github.git.refs["acme/shop"]["heads/main"] == move["sha"]


def test_direct_mode_falls_back_to_a_pull_request_on_a_protected_branch(
    tmp_path: Path, github: FakeGithub
) -> None:
    github.git.protected.add("acme/shop")
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals="direct") as (_, board, ana):
        seen = propose(board, ana, "mark", MARK)
    assert str(seen["output"]).startswith("proposed: https://github.test/acme/shop/pull/")
    assert "would not take a commit on main" in str(seen["output"])
    assert github.git.refs["acme/shop"]["heads/main"] == "commit-acme/shop"


def test_a_person_who_may_not_push_still_gets_an_issue_in_every_mode(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, set(), proposals="direct") as (_, board, ana):
        seen = propose(board, ana, "mark", MARK)
    assert "/issues/" in str(seen["output"])
    assert [tail for tail, *_ in github.git.created] == ["issues"]


@pytest.mark.parametrize("proposals", [None, "direct"])
def test_a_repository_that_moved_creates_nothing(
    tmp_path: Path, github: FakeGithub, proposals: str | None
) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}, proposals=proposals) as (_, board, ana):
        github.git.seed("acme/shop", {"TODO.md": b"- [ ] somebody else's edit.\n"})
        response = operate(board, "add", {"title": "Fresh.", "repository": "shop"}, ana)
    assert response.status == 409
    assert "changed since the board last read it" in json.loads(response.body)["error"]
    assert github.git.created == []
