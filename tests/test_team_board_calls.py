import json
from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest
from board_server import BoardServer, post
from fake_github import FakeGithub, fake_github
from response import Response
from team_board import serve_team_board, sign_in_as
from team_workspace import team_workspace


@pytest.fixture
def github() -> Iterator[FakeGithub]:
    with fake_github(
        {"Ana-Dev": {"acme/shop"}, "bo": {"acme/shop", "acme/vault"}, "Lurker": set()}
    ) as fake:
        yield fake


def operate(
    board: BoardServer, name: str, args: Mapping[str, object], cookie: str = ""
) -> Response:
    """A call as the signed-in page makes it: the session cookie, and no token."""
    return post(
        board,
        f"/api/op/{name}",
        json.dumps(args).encode(),
        Cookie=cookie,
        **{"X-Tadu-Token": ""},
    )


def answer(response: Response) -> dict[str, object]:
    assert response.status == 200
    seen: dict[str, object] = json.loads(response.body)
    return seen


def test_reads_only_show_the_repositories_the_person_reads(
    tmp_path: Path, github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        bo = sign_in_as(board, "bo")
        for name in ("list", "next", "ready", "urgent", "inbox", "feed", "changes", "doctor"):
            seen = answer(operate(board, name, {}, ana))
            assert "vault" not in json.dumps(seen), name
        assert "shop item." in str(answer(operate(board, "list", {}, ana))["output"])
        assert "vault item." in str(answer(operate(board, "list", {}, bo))["output"])


def test_a_repository_the_person_cannot_read_is_unknown_to_every_call(
    tmp_path: Path, github: FakeGithub
) -> None:
    with serve_team_board(team_workspace(tmp_path), github, allow="write") as board:
        ana = sign_in_as(board, "Ana-Dev")
        for name, args in (
            ("show", {"id": "vault item.", "repository": "vault"}),
            ("list", {"repository": "vault"}),
            ("changes", {"repository": "vault"}),
            ("mark", {"id": "x", "repository": "vault", "state": "blocked"}),
        ):
            seen = answer(operate(board, name, args, ana))
            assert seen["code"] != 0, name
            assert "vault item" not in json.dumps(seen), name


def test_a_write_proposes_only_what_the_person_reads(tmp_path: Path, github: FakeGithub) -> None:
    workspace = team_workspace(tmp_path)
    vault = (workspace / "vault" / "TODO.md").read_text()
    github.git.seed("acme/shop", {"TODO.md": (workspace / "shop" / "TODO.md").read_bytes()})
    github.git.pushers["acme/shop"] = {"Ana-Dev"}
    with serve_team_board(workspace, github, allow="write") as board:
        ana = sign_in_as(board, "Ana-Dev")
        refused = answer(
            operate(board, "add", {"title": "Sneaked in.", "repository": "vault"}, ana)
        )
        assert refused["code"] != 0
        assert (workspace / "vault" / "TODO.md").read_text() == vault
        added = answer(operate(board, "add", {"title": "Fresh.", "repository": "shop"}, ana))
        assert added["code"] == 0, added
    assert "proposed:" in str(added["output"])
    assert "Fresh." not in (workspace / "shop" / "TODO.md").read_text()
    assert (workspace / "vault" / "TODO.md").read_text() == vault


def test_writes_follow_allow(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        assert operate(board, "add", {"title": "No.", "repository": "shop"}, ana).status == 403
        assert operate(board, "nope", {}, ana).status == 404


def test_a_call_needs_a_live_session(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        for cookie in ("", "tadu_session=forged"):
            refused = operate(board, "list", {}, cookie)
            assert refused.status == 401
            assert "item" not in refused.body.decode()
        assert post(board, "/api/op/list", b"{}", **{"X-Tadu-Token": board.token}).status == 401


def test_a_call_from_another_origin_is_refused(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github) as board:
        ana = sign_in_as(board, "Ana-Dev")
        for headers in (
            {"Origin": "https://evil.example"},
            {"Sec-Fetch-Site": "same-site"},
            {"Content-Type": "text/plain"},
        ):
            response = post(
                board, "/api/op/list", b"{}", Cookie=ana, **{"X-Tadu-Token": ""}, **headers
            )
            assert response.status in (403, 415), headers


def test_somebody_who_reads_nothing_runs_nothing(tmp_path: Path, github: FakeGithub) -> None:
    with serve_team_board(team_workspace(tmp_path), github, allow="write") as board:
        lurker = sign_in_as(board, "Lurker")
        for name in ("list", "add"):
            assert operate(board, name, {"title": "x", "repository": "shop"}, lurker).status == 403
