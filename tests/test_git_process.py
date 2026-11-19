import shutil
from pathlib import Path

import pytest

from tadu.git_process import git_process
from tadu.history_error import HistoryError


def test_runs_git_in_root(tmp_path: Path) -> None:
    with git_process(tmp_path, ("--version",)) as process:
        out, _ = process.communicate()
    assert out.startswith(b"git version")


def test_without_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)
    with pytest.raises(HistoryError, match="git is not installed"):
        git_process(tmp_path, ("--version",))
