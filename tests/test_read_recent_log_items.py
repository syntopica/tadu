from datetime import date
from pathlib import Path

import pytest

from tadu.read_recent_log_items import read_recent_log_items
from tadu.unreadable_file_error import UnreadableFileError


def test_only_checked_recent_entries(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_text(
        "# TODO Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n\n"
        "- [x] 2026-09-30 — **A:** legacy.\n  - Evidence: old\n"
        "- [x] 2026-10-20 — **A:** recent.\n\n"
        "  ID: t-55161023-f3a9-43a3-94df-589ca752fa13\n  - Evidence: ok\n"
        "- [-] 2026-10-02 — **A:** too old.\n  - Resolution: no\n"
    )
    items = read_recent_log_items(tmp_path, ".", "shop", date(2026, 10, 15))
    assert [(i.state, i.title, i.day) for i in items] == [
        ("x", "**A:** recent.", date(2026, 10, 20))
    ]
    assert items[0].stable


def test_missing_log_is_empty(tmp_path: Path) -> None:
    assert read_recent_log_items(tmp_path, ".", "shop", date(2026, 10, 15)) == ()


def test_subdirectory_path(tmp_path: Path) -> None:
    (tmp_path / "apps/web").mkdir(parents=True)
    (tmp_path / "apps/web/TODO_LOG.md").write_text(
        "- [-] 2026-10-20 — **A:** x.\n  - Resolution: no\n"
    )
    (item,) = read_recent_log_items(tmp_path, "apps/web", "shop", date(2026, 10, 15))
    assert item.path == "apps/web/TODO_LOG.md"


def test_unreadable_log_raises(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_bytes(b"\xff\xfe")
    with pytest.raises(UnreadableFileError):
        read_recent_log_items(tmp_path, ".", "shop", date(2026, 10, 15))


def test_archived_years_follow_the_log_rules(tmp_path: Path) -> None:
    archive = tmp_path / "apps/web/docs/todo-log"
    archive.mkdir(parents=True)
    (tmp_path / "apps/web/TODO_LOG.md").write_text(
        "<!-- tadu:log v1 since 2025-03-01 -->\n- [x] 2026-01-05 — Now.\n  - Evidence: e\n"
    )
    (archive / "2025.md").write_text(
        "- [x] 2025-02-01 — Legacy.\n  - Evidence: e\n- [x] 2025-06-01 — Checked.\n  - Evidence: e\n"
    )
    (archive / "2024.md").write_text("- [x] 2024-06-01 — Too old.\n  - Evidence: e\n")
    (archive / "notes.md").write_text("- [x] 2025-06-02 — Not a year.\n  - Evidence: e\n")
    (archive / "2023.md").mkdir()
    items = read_recent_log_items(tmp_path, "apps/web", "shop", date(2025, 1, 1))
    assert [(i.title, i.path) for i in items] == [
        ("Checked.", "apps/web/docs/todo-log/2025.md"),
        ("Now.", "apps/web/TODO_LOG.md"),
    ]


def test_archive_without_a_log(tmp_path: Path) -> None:
    (tmp_path / "docs/todo-log").mkdir(parents=True)
    (tmp_path / "docs/todo-log/2025.md").write_text("- [x] 2025-06-01 — Kept.\n  - Evidence: e\n")
    (item,) = read_recent_log_items(tmp_path, ".", "shop", date(2025, 1, 1))
    assert item.path == "docs/todo-log/2025.md"
