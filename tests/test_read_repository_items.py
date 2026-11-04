from datetime import date
from pathlib import Path

from tadu.read_repository_items import read_repository_items
from tadu.scan_problem import ScanProblem

CUTOFF = date(2026, 10, 1)


def test_open_items_then_log_items(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    (tmp_path / "TODO_LOG.md").write_text("## 2026\n### 2026-11\n- [x] 2026-11-02 — **C:** Done.\n")
    found = read_repository_items(tmp_path, ".", "shop", CUTOFF)
    assert not isinstance(found, ScanProblem)
    assert [i.state for i in found] == [" ", "x"]


def test_not_a_directory(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    assert read_repository_items(missing, ".", "shop", CUTOFF) == ScanProblem(
        "shop", f"checkout {missing} is not a directory"
    )


def test_unreadable(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"\xff\xfe")
    found = read_repository_items(tmp_path, ".", "shop", CUTOFF)
    assert isinstance(found, ScanProblem)
    assert "could not be read" in found.message
