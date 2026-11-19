from pathlib import Path

from tadu.migration_files import migration_files


def test_todo_log_then_archived_years(tmp_path: Path) -> None:
    (tmp_path / "docs" / "todo-log").mkdir(parents=True)
    for name in ("TODO.md", "TODO_LOG.md", "docs/todo-log/2025.md", "docs/todo-log/2024.md"):
        (tmp_path / name).write_text("x\n")
    assert [name for _, name in migration_files(tmp_path)] == [
        "TODO.md",
        "TODO_LOG.md",
        "docs/todo-log/2024.md",
        "docs/todo-log/2025.md",
    ]
    (tmp_path / "TODO_LOG.md").unlink()
    assert [file for file, _ in migration_files(tmp_path)][:2] == [
        tmp_path / "TODO.md",
        tmp_path / "docs/todo-log/2024.md",
    ]
