from tadu.log_archive_layout import LOG_ARCHIVE_DIR, LOG_ARCHIVE_YEAR_PATTERN


def test_year_files_under_docs_todo_log() -> None:
    assert LOG_ARCHIVE_DIR == ("docs", "todo-log")
    assert LOG_ARCHIVE_YEAR_PATTERN.match("2025.md")
    for name in ("25.md", "2025.txt", "2025.md.bak", "notes.md", "x2025.md"):
        assert not LOG_ARCHIVE_YEAR_PATTERN.match(name), name
