import subprocess
from pathlib import Path

import pytest
from git_checkout import commit_file

from tadu.git_blame_output import git_blame_output


def test_blames_a_committed_file(tmp_path: Path) -> None:
    commit_file(tmp_path, "TODO.md", "- [!] a\n", 1_700_000_000)
    output = git_blame_output(tmp_path, "TODO.md")
    assert output is not None
    assert "committer-time 1700000000" in output


def test_untracked_or_outside_git_is_none(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [!] a\n", encoding="utf-8")
    assert git_blame_output(tmp_path, "TODO.md") is None


def test_without_git_is_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert git_blame_output(tmp_path, "TODO.md") is None


def test_timeout_is_none(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def hang(*_: object, **__: object) -> None:
        raise subprocess.TimeoutExpired(cmd="git", timeout=10)

    monkeypatch.setattr("subprocess.run", hang)
    assert git_blame_output(tmp_path, "TODO.md") is None
