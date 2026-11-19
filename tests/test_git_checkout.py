from pathlib import Path

import pytest
from git_repo import commit, git, git_repo

from tadu.git_checkout import git_checkout
from tadu.history_error import HistoryError


def test_top_and_subdirectory(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    (root / "docs").mkdir()
    assert git_checkout(root) == ("", False)
    assert git_checkout(root / "docs") == ("docs/", False)


def test_shallow_clone(tmp_path: Path) -> None:
    origin = git_repo(tmp_path / "origin")
    commit(origin, {"a.md": "a\n"}, "One")
    commit(origin, {"a.md": "b\n"}, "Two")
    git(tmp_path, "clone", "-q", "--depth", "1", origin.as_uri(), "clone")
    assert git_checkout(tmp_path / "clone") == ("", True)


def test_not_a_repository(tmp_path: Path) -> None:
    with pytest.raises(HistoryError, match="not a git repository"):
        git_checkout(tmp_path)
