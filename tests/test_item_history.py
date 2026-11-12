from pathlib import Path

import pytest

from tadu.item_history import item_history


def test_not_a_repository(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    assert item_history(tmp_path, "TODO.md", 1, 1) is None


def test_git_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    assert item_history(tmp_path, "TODO.md", 1, 1) is None
