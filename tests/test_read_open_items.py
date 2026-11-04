from pathlib import Path

import pytest

from tadu.read_open_items import read_open_items
from tadu.unreadable_file_error import UnreadableFileError


def test_missing_todo_is_unreadable(tmp_path: Path) -> None:
    with pytest.raises(UnreadableFileError, match=r"no TODO\.md"):
        read_open_items(tmp_path, ".", "shop")


def test_backlog_in_subdirectory_has_relative_path(tmp_path: Path) -> None:
    (tmp_path / "apps/web").mkdir(parents=True)
    (tmp_path / "apps/web/TODO.md").write_text("- [ ] A.\n- [x] Done.\n")
    (item,) = read_open_items(tmp_path, "apps/web", "shop")
    assert item.path == "apps/web/TODO.md"


def test_root_backlog_path(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [!] A.\n")
    assert read_open_items(tmp_path, ".", "shop")[0].path == "TODO.md"
