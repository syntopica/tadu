import json
from datetime import date
from pathlib import Path

from fake_github import FakeGithub, fake_github
from storefront_workspace import STOREFRONT_WORKSPACE
from team_workspace import team_workspace

from tadu.board_payload import board_payload
from tadu.board_session import BoardSession
from tadu.board_state import BoardState
from tadu.cli import main
from tadu.local_config import LocalConfig
from tadu.payload_view import PayloadView
from tadu.signed_in_view import signed_in_view
from tadu.workspace import Workspace

TODAY = date(2026, 11, 4)


def payload(github: FakeGithub, workspace: Path, login: str) -> dict[str, object]:
    sign_in = github.sign_in()
    state = BoardState(workspace, 14, "t", frozenset(), "read", main, sign_in)
    session = BoardSession(f"s-{login}", login, 10**12, f"tok-{login}")

    def narrow(workspace: Workspace, local: LocalConfig) -> PayloadView:
        return signed_in_view(sign_in, session, workspace, local)

    return board_payload(state, 14, TODAY, narrow)


def test_only_the_readable_repositories_reach_the_page(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    with fake_github({"Ana-Dev": {"acme/shop"}}) as github:
        seen = payload(github, workspace, "Ana-Dev")
    assert [c["title"] for c in seen["cards"]] == ["shop item."]  # type: ignore[attr-defined]
    assert seen["workspace"] == STOREFRONT_WORKSPACE
    assert seen["views"] == [{"name": "mine", "criteria": "assignee=ana"}]
    assert seen["problems"] == []
    assert (seen["user"], seen["me"]) == ("Ana-Dev", "ana")
    text = json.dumps(seen)
    for hidden in ("vault", "treasury", "bigbank", "Big Bank", "money", "notes", "site"):
        assert hidden not in text.lower()


def test_me_is_the_login_not_the_machine(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    local = workspace / "tadu-workspace.local.toml"
    local.write_text(
        local.read_text().replace('me = "bo"\n', 'me = "bo"\neditor_url = "x://{path}"\n')
    )
    with fake_github({"stranger": {"acme/shop", "acme/vault"}}) as github:
        seen = payload(github, workspace, "stranger")
    assert seen["me"] is None
    assert seen["user"] == "stranger"
    assert sorted(c["repository"] for c in seen["cards"]) == ["shop", "vault"]  # type: ignore[attr-defined]
    assert [c["waiting_on_me"] for c in seen["cards"]] == [False, False]  # type: ignore[attr-defined]
    assert [c["editor_url"] for c in seen["cards"]] == [None, None]  # type: ignore[attr-defined]
    assert str(tmp_path) not in json.dumps(seen)


def test_nobody_reads_what_github_does_not_know(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    with fake_github({}) as github:
        seen = payload(github, workspace, "Ana-Dev")
    assert seen["cards"] == []
    assert seen["workspace"] == {"organizations": [], "projects": [], "repositories": []}


def test_a_failed_check_is_a_problem_naming_no_repository(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    toml = workspace / "tadu-workspace.toml"
    toml.write_text(toml.read_text().replace("acme/shop", "acme/flaky"))
    with fake_github({}) as github:
        seen = payload(github, workspace, "Ana-Dev")
    assert seen["cards"] == []
    assert seen["problems"] == [
        {
            "repository": "GitHub",
            "message": "GitHub answered HTTP 502, so some repositories are hidden until Reload "
            "can check them",
        }
    ]


def test_an_unreachable_github_is_a_problem(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    with fake_github({}) as github:
        gone = FakeGithub(github.url, {})
    seen = payload(gone, workspace, "Ana-Dev")
    problems = seen["problems"]
    assert isinstance(problems, list)
    assert problems[0]["message"].startswith("GitHub could not be reached, so")


def test_scan_problems_of_hidden_repositories_stay_hidden(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    (tmp_path / "vault" / "TODO.md").unlink()
    (tmp_path / "shop" / "TODO.md").unlink()
    with fake_github({"Ana-Dev": {"acme/shop"}}) as github:
        seen = payload(github, workspace, "Ana-Dev")
    problems = seen["problems"]
    assert isinstance(problems, list)
    assert [p["repository"] for p in problems] == ["shop"]


def test_without_a_session_the_payload_is_whole(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    with fake_github({}) as github:
        state = BoardState(workspace, 14, "t", frozenset(), "read", main, github.sign_in())
        seen = board_payload(state, 14, TODAY)
        assert github.requests == []
    assert len(seen["cards"]) == 4  # type: ignore[arg-type]
    assert (seen["user"], seen["me"]) == (None, "bo")
    local = workspace / "tadu-workspace.local.toml"
    local.write_text(
        local.read_text().replace('me = "bo"\n', 'me = "bo"\neditor_url = "x://{path}"\n')
    )
    assert board_payload(state, 14, TODAY)["cards"][0]["editor_url"].startswith("x://")  # type: ignore[index]
