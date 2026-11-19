import json
from pathlib import Path

import pytest

from tadu.cli import main
from tadu.migration_files import migration_files
from tadu.migration_tasks import migration_tasks

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
ARCHIVED = (
    f"# TODO Log 2025\n\n- [x] 2025-06-01 — **Core:** Archived.\n\n  ID: {ID}\n  - Evidence: CI.\n"
)


def backlog(root: Path) -> Path:
    (root / "docs/todo-log").mkdir(parents=True)
    (root / "TODO.md").write_text("# TODO\n\n- [ ] Open.\n")
    (root / "TODO_LOG.md").write_text(
        "# TODO Log\n\n- [x] 2026-01-02 — Logged.\n  - Evidence: e.\n"
    )
    (root / "docs/todo-log/2025.md").write_text(ARCHIVED)
    (root / "docs/todo-log/2024.md").write_text(
        "- [-] 2024-03-01 — Dropped.\n  - Resolution: no.\n"
    )
    (root / "docs/todo-log/README.md").write_text("- [ ] Not a year.\n")
    return root


def test_files_in_order(tmp_path: Path) -> None:
    root = backlog(tmp_path)
    assert [name for _, name in migration_files(root)] == [
        "TODO.md",
        "TODO_LOG.md",
        "docs/todo-log/2024.md",
        "docs/todo-log/2025.md",
    ]
    (root / "TODO_LOG.md").unlink()
    assert [name for _, name in migration_files(root)][:2] == ["TODO.md", "docs/todo-log/2024.md"]


def test_archived_years_become_closed_tasks(tmp_path: Path) -> None:
    tasks, _ = migration_tasks(backlog(tmp_path))
    assert [(task["title"], task["state"]) for task in tasks] == [
        ("Open", "pending"),
        ("Logged", "done"),
        ("Dropped", "cancelled"),
        ("Archived", "done"),
    ]
    assert tasks[3]["id"] == ID


def test_command_converts_and_removes_them(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = backlog(tmp_path)
    assert main(["migrate", str(root)]) == 0
    assert "then remove TODO.md, TODO_LOG.md, docs/todo-log/2024.md, docs/todo-log/2025.md" in (
        capsys.readouterr().out
    )
    assert main(["migrate", str(root), "--write"]) == 0
    assert "removed TODO.md, TODO_LOG.md, docs/todo-log/2024.md" in capsys.readouterr().out
    task = json.loads((root / f"todo/closed/{ID}.json").read_text())
    assert (task["title"], task["closed"]) == ("Archived", "2025-06-01")
    assert sorted(p.name for p in (root / "docs/todo-log").iterdir()) == ["README.md"]


def test_a_field_line_is_a_field_in_a_log_item_too(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "TODO_LOG.md").write_text(
        f"- [x] 2026-01-02 — Closed.\n\n  Priority: high\n\n  ID: {ID}\n  - Result: r.\n  - Evidence: e.\n"
        "- [x] 2026-01-03 — Prose.\n\n  Priority: low\n  Not a field after it.\n"
    )
    (closed, prose), _ = migration_tasks(tmp_path)
    assert (closed["id"], closed["priority"], closed["notes"], closed["result"]) == (
        ID,
        "high",
        [],
        "r.",
    )
    assert (prose["priority"], prose["notes"]) == ("low", ["Not a field after it."])
