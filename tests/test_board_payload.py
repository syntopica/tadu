from datetime import date
from pathlib import Path

import pytest
from board_workspace import board_workspace

from tadu.board_payload import board_payload
from tadu.board_state import BoardState
from tadu.workspace_error import WorkspaceError
from tadu.workspace_id import workspace_id

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
    assert payload["done_days"] == 14
    assert payload["workspace_id"] == workspace_id(tmp_path)
    assert payload["workspace"] == {
        "organizations": [{"id": "acme", "name": "Acme"}],
        "projects": [
            {
                "key": "storefront",
                "name": "storefront",
                "repositories": ["shop"],
                "roles": [{"role": "client", "org": "acme"}],
            }
        ],
        "repositories": [{"key": "shop"}],
    }
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


def test_workspace_without_projects(tmp_path: Path) -> None:
    repo = tmp_path / "solo"
    repo.mkdir()
    (repo / "TODO.md").write_text("- [ ] Only item.\n")
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "solo"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nsolo = "{repo}"\n')
    payload = board_payload(state(tmp_path), TODAY)
    assert payload["me"] is None
    assert [c["project"] for c in payload["cards"]] == [None]  # type: ignore[attr-defined]
    assert payload["workspace"] == {
        "organizations": [],
        "projects": [],
        "repositories": [{"key": "solo"}],
    }
