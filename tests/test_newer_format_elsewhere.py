"""A backlog in a newer format stops only what reads it: other paths and repositories go on."""

import json
from datetime import date
from pathlib import Path

import pytest
from a11y_workspace import a11y_workspace
from board_states import board_state
from task_backlog import task_backlog

from tadu.board_call import board_call
from tadu.board_payload import board_payload
from tadu.cli import main

NEWER = {"tadu": 3, "categories": {"core": "Core"}}
UPGRADE = "written in tadu format 3"


def upgrade_tasks(workspace: Path) -> None:
    """A teammate upgraded the workspace's `tasks` repository to format 3."""
    (workspace / "tasks" / "todo" / "tadu.json").write_text(json.dumps(NEWER))


def test_a_command_inside_a_newer_checkout_reads_the_path_it_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(task_backlog(tmp_path / "newer", [], NEWER))
    other = tmp_path / "other"
    other.mkdir()
    (other / "TODO.md").write_text("- [ ] Elsewhere.\n")
    assert main(["list", str(other)]) == 0
    assert "Elsewhere." in capsys.readouterr().out
    assert main(["list"]) == 2
    assert UPGRADE in capsys.readouterr().err


def test_a_workspace_command_names_the_newer_repository_and_lists_the_rest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = a11y_workspace(tmp_path)
    upgrade_tasks(workspace)
    main(["list", "--workspace", str(workspace)])
    out, err = capsys.readouterr()
    assert "Fix the cart total." in out
    assert "Read only item." in out
    assert "tasks" in err
    assert UPGRADE in err


def test_the_board_shows_the_rest_and_refuses_a_change_by_name(tmp_path: Path) -> None:
    workspace = a11y_workspace(tmp_path)
    upgrade_tasks(workspace)
    payload = board_payload(board_state(workspace), 14, date(2026, 11, 4))
    (problem,) = payload["problems"]  # type: ignore[misc]
    assert problem["repository"] == "tasks"
    assert UPGRADE in problem["message"]
    assert payload["formats"] == {"shop": 1, "ro": 1}
    arguments = {"title": "T", "repository": "tasks", "category": "core"}
    status, body, _ = board_call(
        "/api/op/add", json.dumps(arguments).encode(), board_state(workspace, "write")
    )
    answered = json.loads(body)
    assert (status, answered["code"]) == (200, 2), answered
    assert UPGRADE in answered["errors"]
    assert sorted(p.name for p in (workspace / "tasks" / "todo").iterdir()) == ["open", "tadu.json"]
