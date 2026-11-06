import json
from datetime import date
from pathlib import Path

from board_workspace import board_workspace

from tadu.board_route import board_route
from tadu.board_state import BoardState

TODAY = date(2026, 11, 4)


def state(workspace: Path) -> BoardState:
    return BoardState(workspace, 14, "t", frozenset())


def test_index_and_assets(tmp_path: Path) -> None:
    assert board_route("/", state(tmp_path), TODAY)[::2] == (200, "text/html; charset=utf-8")
    assert board_route("/app.js", state(tmp_path), TODAY)[2].startswith("text/javascript")
    assert board_route("/card-visible.js", state(tmp_path), TODAY)[2].startswith("text/javascript")
    assert board_route("/board.css", state(tmp_path), TODAY)[2].startswith("text/css")


def test_cards(tmp_path: Path) -> None:
    status, body, content_type = board_route("/api/cards", state(board_workspace(tmp_path)), TODAY)
    assert (status, content_type) == (200, "application/json; charset=utf-8")
    assert json.loads(body)["cards"][0]["title"] == "<script>alert(1)</script>"


def test_workspace_error_is_500_json(tmp_path: Path) -> None:
    status, body, _ = board_route("/api/cards", state(tmp_path), TODAY)
    assert status == 500
    assert "tadu-workspace.toml" in json.loads(body)["error"]


def test_unknown_paths(tmp_path: Path) -> None:
    for path in (
        "/index.html",
        "/api",
        "/board.css/",
        "/../pyproject.toml",
        "/missing.js",
        "/a/b.js",
    ):
        assert board_route(path, state(tmp_path), TODAY)[0] == 404
