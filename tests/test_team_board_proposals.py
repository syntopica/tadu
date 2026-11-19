import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from board_server import BoardServer
from fake_github import FakeGithub, fake_github
from team_board import serve_team_board, sign_in_as
from team_workspace import team_workspace
from test_team_board_calls import answer, operate

from tadu.captured_run import INTERNAL_ERROR


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github(
        {"Ana-Dev": {"acme/shop"}, "bo": {"acme/shop", "acme/vault"}, "Lurker": set()}
    ) as fake:
        yield fake


def seeded(github: FakeGithub, workspace: Path, pushers: set[str]) -> None:
    """GitHub holds the shop's files as the checkout has them; `pushers` may push to it."""
    shop = workspace / "shop"
    github.git.seed("acme/shop", {p.name: p.read_bytes() for p in sorted(shop.glob("TODO*.md"))})
    github.git.pushers["acme/shop"] = pushers


@contextmanager
def signed_in(
    tmp_path: Path, github: FakeGithub, pushers: set[str], login: str = "Ana-Dev"
) -> Iterator[tuple[Path, BoardServer, str]]:
    """A writing team board over a workspace GitHub holds as it is, and a person signed in."""
    workspace = team_workspace(tmp_path)
    (workspace / "shop" / "TODO_LOG.md").write_text("")
    seeded(github, workspace, pushers)
    with serve_team_board(workspace, github, allow="write") as board:
        yield workspace, board, sign_in_as(board, login)


def snapshot(workspace: Path) -> dict[str, bytes]:
    """Every file but the board's own memory of sessions."""
    files = [p for p in sorted(workspace.rglob("*")) if p.is_file() and p.suffix != ".json"]
    return {str(p): p.read_bytes() for p in files}


def posted(github: FakeGithub, kind: str) -> list[dict[str, object]]:
    return [body for tail, _, _, body in github.git.created if tail == kind]


def propose(
    board: BoardServer, cookie: str, name: str, args: dict[str, object]
) -> dict[str, object]:
    return answer(operate(board, name, args | {"repository": "shop"}, cookie))


def test_a_writer_gets_one_commit_on_a_new_branch_and_one_pull_request(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        seen = propose(
            board, ana, "mark", {"match": "shop item", "state": "blocked", "note": "waiting"}
        )
    assert seen["code"] == 0, seen
    assert str(seen["output"]).startswith("proposed: https://github.test/acme/shop/pull/")
    assert seen["errors"] == ""
    assert [tail for tail, *_ in github.git.created] == [
        "git/trees",
        "git/commits",
        "git/refs",
        "pulls",
    ]
    (ref,) = posted(github, "git/refs")
    assert str(ref["ref"]).startswith("refs/heads/tadu/mark-")
    (pull,) = posted(github, "pulls")
    assert pull["base"] == "main"
    assert pull["head"] == str(ref["ref"]).removeprefix("refs/heads/")
    (tree,) = posted(github, "git/trees")
    assert [(e["path"], "waiting" in e["content"]) for e in tree["tree"]] == [("TODO.md", True)]  # type: ignore[attr-defined]


def test_the_server_checkout_stays_byte_identical(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (workspace, board, ana):
        before = snapshot(workspace)
        added = propose(board, ana, "add", {"title": "Fresh."})
        closed = propose(board, ana, "close", {"match": "shop item", "evidence": "done"})
        after = snapshot(workspace)
    assert added["code"] == 0, added
    assert closed["code"] == 0, closed
    assert after == before
    assert len(posted(github, "pulls")) == 2


def test_somebody_who_cannot_push_gets_an_issue_with_the_diff(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, set()) as (_, board, ana):
        seen = propose(board, ana, "add", {"title": "Fresh."})
    assert seen["code"] == 0, seen
    assert "https://github.test/acme/shop/issues/" in str(seen["output"])
    assert [tail for tail, *_ in github.git.created] == ["issues"]
    (issue,) = posted(github, "issues")
    assert "Fresh." in str(issue["body"])
    assert "+++ b/TODO.md" in str(issue["body"])
    assert "add" in str(issue["title"])


def test_a_repository_that_moved_creates_nothing(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        github.git.seed("acme/shop", {"TODO.md": b"- [ ] somebody else's edit.\n"})
        response = operate(board, "add", {"title": "Fresh.", "repository": "shop"}, ana)
    assert response.status == 409
    assert "changed since the board last read it" in json.loads(response.body)["error"]
    assert github.git.created == []


def test_no_write_ever_targets_the_default_branch(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        propose(board, ana, "add", {"title": "Fresh."})
    assert github.git.refs["acme/shop"]["heads/main"] == "commit-acme/shop"
    assert all(str(body.get("ref", "")) != "refs/heads/main" for body in posted(github, "git/refs"))
    writes = [r for r in github.requests if not r.startswith("GET ") and "/api/repos/" in r]
    assert writes
    assert all(r.startswith("POST ") for r in writes)
    assert not any(r.endswith("heads/main") for r in writes)


def test_a_preview_never_reaches_github(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        github.requests.clear()
        seen = propose(board, ana, "add", {"title": "Fresh.", "preview": True})
    assert seen["code"] == 0, seen
    assert "Fresh." in str(seen["output"])
    assert github.git.created == []
    assert not any(r.startswith("POST /api/repos/") or "/git/" in r for r in github.requests)


def test_reads_still_run_on_the_checkout(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        seen = propose(board, ana, "list", {})
    assert "shop item." in str(seen["output"])
    assert github.git.created == []


def test_a_person_without_access_gets_the_same_refusal(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        refused = answer(operate(board, "add", {"title": "x", "repository": "vault"}, ana))
        unknown = answer(operate(board, "add", {"title": "x", "repository": "ghost"}, ana))
        lurker = operate(
            board, "add", {"title": "x", "repository": "shop"}, sign_in_as(board, "Lurker")
        )
    assert refused["code"] != 0
    assert "vault item" not in json.dumps(refused)
    assert refused["errors"] == str(unknown["errors"]).replace("ghost", "vault")
    assert lurker.status == 403
    assert github.git.created == []


def test_github_refusing_a_step_answers_a_short_error_and_no_server_path(
    tmp_path: Path, github: FakeGithub
) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (workspace, board, ana):
        github.git.pushers["acme/shop"] = set()
        github.git.pushers["acme/shop"].add("Ana-Dev")
        github.git.refs.clear()
        seen = propose(board, ana, "add", {"title": "Fresh."})
    assert seen["code"] == 2
    assert "status 404" in str(seen["errors"])
    assert str(workspace) not in json.dumps(seen)
    assert "tadu-proposal" not in json.dumps(seen)


def test_a_bad_repository_argument_is_refused(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        seen = answer(operate(board, "add", {"title": "x", "repository": 5}, ana))
    assert seen["code"] != 0
    assert github.git.created == []


def test_a_change_that_fails_proposes_nothing(tmp_path: Path, github: FakeGithub) -> None:
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        seen = propose(board, ana, "close", {"match": "nothing like it", "evidence": "x"})
    assert seen["code"] != 0
    assert github.git.created == []


def test_an_internal_error_answers_no_detail(
    tmp_path: Path, github: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "tadu.propose_call.run_on_copy", lambda *_: ((INTERNAL_ERROR, "", "/secret"), [])
    )
    with signed_in(tmp_path, github, {"Ana-Dev"}) as (_, board, ana):
        seen = propose(board, ana, "add", {"title": "x"})
    assert seen["errors"] == "tadu add: internal error\n"
