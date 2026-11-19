from datetime import date
from pathlib import Path

import pytest
from changes_repo import ID, OTHER, changes_repo
from git_repo import commit, git_repo
from sample_task import sample_task

from tadu.canonical_task_text import canonical_task_text
from tadu.change_repository import ChangeRepository
from tadu.history_error import HistoryError
from tadu.repository_changes import repository_changes


def events(root: Path, since: date, until: date, backlog: str = ".") -> list[tuple[str, str, str]]:
    entries = repository_changes(ChangeRepository("shop", "store", root, backlog), since, until)
    assert {entry["project"] for entry in entries} <= {"store"}
    return [((entry["date"] or "")[:10], entry["event"], entry["key"] or "") for entry in entries]


def test_every_kind_of_change_of_a_markdown_backlog(tmp_path: Path) -> None:
    root = changes_repo(tmp_path / "shop")
    assert events(root, date(2026, 11, 1), date(2026, 11, 30)) == [
        ("2026-11-08", "removed", OTHER),
        ("2026-11-07", "cancelled", ID),
        ("2026-11-06", "reopened", ID),
        ("2026-11-05", "closed", ID),
        ("2026-11-04", "blocked", ID),
        ("2026-11-03", "started", ID),
        ("2026-11-02", "changed", ID),
        ("2026-11-01", "created", ID),
        ("2026-11-01", "created", OTHER),
    ]


def test_only_the_days_asked_for(tmp_path: Path) -> None:
    root = changes_repo(tmp_path / "shop")
    assert [event for _, event, _ in events(root, date(2026, 11, 3), date(2026, 11, 5))] == [
        "closed",
        "blocked",
        "started",
    ]
    assert events(root, date(2026, 12, 1), date(2026, 12, 31)) == []


def test_tasks_and_the_commit_that_migrated_them(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"app/TODO.md": f"- [ ] A.\n\n  ID: {ID}\n"}, "Add")
    task = sample_task(1, id=ID, title="A")
    migrated = {
        "app/TODO.md": "",
        "app/todo/tadu.json": "{}\n",
        f"app/todo/open/{ID}.json": canonical_task_text(task),
    }
    commit(root, migrated, "Migrate")
    done = sample_task(1, "done", id=ID, title="A")
    commit(
        root,
        {f"app/todo/open/{ID}.json": "", f"app/todo/closed/{ID}.json": canonical_task_text(done)},
        "Close",
    )
    assert events(root, date(2026, 11, 1), date(2026, 11, 30), "app") == [
        ("2026-11-03", "closed", ID),
        ("2026-11-02", "migrated", ID),
        ("2026-11-01", "created", ID),
    ]


def test_outside_git(tmp_path: Path) -> None:
    with pytest.raises(HistoryError):
        repository_changes(
            ChangeRepository("shop", None, tmp_path), date(2026, 11, 1), date(2026, 11, 30)
        )
