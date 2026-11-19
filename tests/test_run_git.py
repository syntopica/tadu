from pathlib import Path

import pytest
from git_repo import commit, git_repo

from tadu.history_error import HistoryError
from tadu.run_git import run_git


def test_output_and_standard_input(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    assert run_git(root, ("hash-object", "--stdin"), "a\n").strip() == (
        "78981922613b2afb6025042ff6bd878ac1994e85"
    )


def test_failure_names_what_git_said(tmp_path: Path) -> None:
    with pytest.raises(HistoryError) as raised:
        run_git(tmp_path, ("rev-parse", "--show-prefix"))
    assert str(raised.value).startswith("not a git repository")


def test_silent_failure(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"a.md": "a\n"}, "Add a")
    (root / "a.md").write_text("b\n")
    with pytest.raises(HistoryError, match=r"^git diff failed$"):
        run_git(root, ("diff", "--quiet"))
