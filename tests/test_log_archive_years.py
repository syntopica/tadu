from pathlib import Path

from tadu.log_archive_years import log_archive_years


def test_year_files_from_a_year_on(tmp_path: Path) -> None:
    archive = tmp_path / "app" / "docs" / "todo-log"
    archive.mkdir(parents=True)
    for name in ("2023.md", "2025.md", "2024.md", "notes.md", "2026.txt"):
        (archive / name).write_text("x\n")
    (archive / "2027.md").mkdir()
    found = log_archive_years(tmp_path, "app", 2024)
    assert [(file.name, path) for file, path in found] == [
        ("2024.md", "app/docs/todo-log/2024.md"),
        ("2025.md", "app/docs/todo-log/2025.md"),
    ]
    paths = [path for _, path in log_archive_years(tmp_path / "app", ".", 0)]
    assert paths == ["docs/todo-log/2023.md", "docs/todo-log/2024.md", "docs/todo-log/2025.md"]


def test_no_archive(tmp_path: Path) -> None:
    assert log_archive_years(tmp_path, ".", 0) == []
