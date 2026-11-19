from pathlib import Path

from git_repo import commit, git_repo

from tadu.log_archive_years_at import log_archive_years_at


def test_years_of_a_commit(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    files = {"app/docs/todo-log/2025.md": "a\n", "app/docs/todo-log/2024.md": "b\n"}
    first = commit(root, {**files, "app/docs/todo-log/notes.md": "c\n"}, "Archive")
    commit(root, {"app/docs/todo-log/2023.md": "d\n"}, "Older")
    assert log_archive_years_at(root, first, "app") == [
        "app/docs/todo-log/2024.md",
        "app/docs/todo-log/2025.md",
    ]
    assert log_archive_years_at(root / "app", first, ".") == [
        "docs/todo-log/2024.md",
        "docs/todo-log/2025.md",
    ]
    assert log_archive_years_at(root, first, "other") == []
