import json
from datetime import date
from pathlib import Path

from board_states import board_state
from board_workspace import board_workspace

from tadu.board_cards import board_cards

TODAY = date(2026, 11, 4)


def test_cards_as_json(tmp_path: Path) -> None:
    status, body, content_type = board_cards(board_state(board_workspace(tmp_path)), "", TODAY)
    assert (status, content_type) == (200, "application/json; charset=utf-8")
    payload = json.loads(body)
    assert [card["title"] for card in payload["cards"]] == [
        "<script>alert(1)</script>",
        "Blocked on ana.",
    ]
    assert payload["done_days"] == 14


def test_a_workspace_that_does_not_load(tmp_path: Path) -> None:
    status, body, _ = board_cards(board_state(tmp_path), "", TODAY)
    assert status == 500
    assert "tadu-workspace.toml" in json.loads(body)["error"]


def test_a_done_window_of_whole_days(tmp_path: Path) -> None:
    state = board_state(board_workspace(tmp_path), "write")
    payload = json.loads(board_cards(state, "done_days=0", TODAY)[1])
    assert (payload["done_days"], payload["allow"], payload["today"]) == (0, "write", "2026-11-04")
    assert payload["writable"] == ["shop"]
    reading = json.loads(board_cards(board_state(tmp_path), "", TODAY)[1])
    assert reading["writable"] == []
    for bad in ("done_days=-1", "done_days=x", "done_days=36501", "done_days=%C2%B2"):
        status, body, _ = board_cards(state, bad, TODAY)
        assert (status, json.loads(body)) == (400, {"error": "done_days must be 0 to 36500"})
