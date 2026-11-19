import json
from pathlib import Path

from board_server import BoardServer, post, serve_board
from board_workspace import board_workspace
from changes_workspace import changes_workspace
from history_workspace import ID, history_workspace
from response import Response

from tadu.board_body_limit import BOARD_BODY_LIMIT


def call(board: BoardServer, name: str, arguments: object, **headers: str) -> Response:
    return post(board, f"/api/op/{name}", json.dumps(arguments).encode(), **headers)


def answer(response: Response) -> dict[str, object]:
    assert response.status == 200, response.body
    found = json.loads(response.body)
    assert isinstance(found, dict)
    return found


def test_a_read_only_board_runs_reads_only(tmp_path: Path) -> None:
    with serve_board(board_workspace(tmp_path)) as board:
        listed = answer(call(board, "list", {"json": True}))
        assert listed["code"] == 0
        lines = str(listed["output"]).splitlines()
        assert json.loads(lines[0])["title"] == "<script>alert(1)</script>"
        refused = call(board, "add", {"title": "T"})
        assert refused.status == 403
        assert "allows read only" in json.loads(refused.body)["error"]
        for path in ("/api/op/nope", "/api/op/board", "/api/op/", "/api/cards", "/"):
            assert post(board, path, b"{}").status == 404


def test_only_the_page_itself_may_call(tmp_path: Path) -> None:
    with serve_board(board_workspace(tmp_path)) as board:
        body = b"{}"
        refusals = {
            421: [{"Host": "evil.example:80"}],
            403: [
                {"X-Tadu-Token": ""},
                {"X-Tadu-Token": "nope"},
                {"Origin": "http://evil.example"},
                {"Origin": "null"},
                {"Sec-Fetch-Site": "cross-site"},
                {"Sec-Fetch-Site": "same-site"},
            ],
            415: [{"Content-Type": "text/plain"}, {"Content-Type": ""}],
            411: [{"Content-Length": ""}, {"Content-Length": "\u00b2"}],
            413: [{"Content-Length": str(BOARD_BODY_LIMIT + 1)}],
        }
        for status, variants in refusals.items():
            for headers in variants:
                assert post(board, "/api/op/list", body, **headers).status == status, headers
        query = post(board, f"/api/op/list?token={board.token}", body, **{"X-Tadu-Token": ""})
        assert query.status == 403
        assert post(board, "/api/op/list", body, **{"Sec-Fetch-Site": "same-origin"}).status == 200
        assert post(board, "/api/op/list", body, Origin="").status == 200
        for bad in (b"[]", b"not json", b"\xff", b"[" * 60000):
            assert post(board, "/api/op/list", bad).status == 400


def test_a_writable_board_changes_files_within_the_repository_access(tmp_path: Path) -> None:
    workspace = board_workspace(tmp_path)
    with serve_board(workspace, "write") as board:
        previewed = answer(call(board, "add", {"title": "Ship it.", "preview": True}))
        assert (previewed["code"], "Ship it." in (tmp_path / "shop" / "TODO.md").read_text()) == (
            0,
            False,
        )
        added = answer(call(board, "add", {"title": "Ship it.", "repository": "shop"}))
        assert added["code"] == 0
        assert "Ship it." in (tmp_path / "shop" / "TODO.md").read_text()
        assert call(board, "archive", {}).status == 403
        wrong = answer(call(board, "add", {"title": 3}))
        assert (wrong["code"], wrong["errors"]) == (2, "title must be a string")
    text = (workspace / "tadu-workspace.toml").read_text()
    (workspace / "tadu-workspace.toml").write_text(
        text.replace('key = "shop"\n', 'key = "shop"\naccess = "read"\n')
    )
    with serve_board(workspace, "admin") as board:
        refused = answer(call(board, "add", {"title": "Again."}))
        assert refused["code"] == 2
        assert "repository shop allows read only, and this needs write" in str(refused["errors"])


def test_history_and_changes_are_calls_too(tmp_path: Path) -> None:
    with serve_board(history_workspace(tmp_path / "h")) as board:
        arguments = {"key": ID, "repository": "shop", "history": True, "json": True}
        shown = answer(call(board, "show", arguments))
        assert len(json.loads(str(shown["output"]))["history"]) == 2
    with serve_board(changes_workspace(tmp_path / "c")) as board:
        arguments = {"since": "2026-11-01", "until": "2026-11-30", "json": True}
        changes = answer(call(board, "changes", arguments))
        assert len(str(changes["output"]).splitlines()) == 9
