from datetime import date
from pathlib import Path

import pytest
from board_workspace import ITEMS, board_workspace
from git_checkout import commit_file

from tadu.board_payload import board_payload
from tadu.board_state import BoardState
from tadu.local_date import local_date
from tadu.workspace_error import WorkspaceError

TODAY = date(2026, 11, 4)


def state(workspace: Path) -> BoardState:
    return BoardState(workspace, 14, "t", frozenset())


def test_cards_me_columns_and_time(tmp_path: Path) -> None:
    payload = board_payload(state(board_workspace(tmp_path)), TODAY)
    assert [c["title"] for c in payload["cards"]] == [  # type: ignore[attr-defined]
        "<script>alert(1)</script>",
        "Blocked on ana.",
    ]
    assert payload["me"] == "ana"
    assert payload["problems"] == []
    assert payload["columns"] == ["backlog", "ready", "in_progress", "blocked", "done", "cancelled"]
    assert str(payload["generated_at"]).startswith("20")


def test_rescans_and_reports_problems(tmp_path: Path) -> None:
    workspace = board_workspace(tmp_path)
    (tmp_path / "shop" / "TODO.md").unlink()
    payload = board_payload(state(workspace), TODAY)
    assert payload["cards"] == []
    problems = payload["problems"]
    assert isinstance(problems, list)
    assert [p["repository"] for p in problems] == ["shop"]
    assert problems[0]["message"]


def test_bad_workspace_raises(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError):
        board_payload(state(tmp_path), TODAY)


def test_ages_blocked_cards_from_git(tmp_path: Path) -> None:
    workspace = board_workspace(tmp_path)
    stamp = 1_700_000_000
    commit_file(tmp_path / "shop", "TODO.md", ITEMS, stamp)
    cards = board_payload(state(workspace), TODAY)["cards"]
    assert isinstance(cards, list)
    open_card, blocked = cards
    since = local_date(stamp)
    assert (open_card["blocked_since"], open_card["blocked_days"]) == (None, None)
    assert blocked["blocked_since"] == since.isoformat()
    assert blocked["blocked_days"] == (TODAY - since).days
