import subprocess
from pathlib import Path

import pytest

from tadu.item_history import item_history


def test_not_a_repository(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] A.\n")
    assert item_history(tmp_path, "TODO.md", 1, 1) is None


def test_git_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    assert item_history(tmp_path, "TODO.md", 1, 1) is None


def git(root: Path, *args: str) -> None:
    base = ["git", "-C", str(root), "-c", "user.name=T", "-c", "user.email=t@example.com"]
    subprocess.run([*base, *args], check=True, capture_output=True)  # noqa: S603


def committed_repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    (tmp_path / "TODO.md").write_text("- [ ] A.\n- [ ] B.\n")
    git(tmp_path, "add", "TODO.md")
    git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


def test_committed_item(tmp_path: Path) -> None:
    root = committed_repo(tmp_path)
    history = item_history(root, "TODO.md", 2, 2)
    assert history is not None
    assert history.endswith(" T first\n")


def test_uncommitted_insertion_is_refused(tmp_path: Path) -> None:
    root = committed_repo(tmp_path)
    (root / "TODO.md").write_text("- [ ] New.\n- [ ] A.\n- [ ] B.\n")
    assert item_history(root, "TODO.md", 1, 1) is None
    assert item_history(root, "TODO.md", 3, 3) is None


def test_untracked_file_is_refused(tmp_path: Path) -> None:
    root = committed_repo(tmp_path)
    (root / "OTHER.md").write_text("- [ ] C.\n")
    assert item_history(root, "OTHER.md", 1, 1) is None
