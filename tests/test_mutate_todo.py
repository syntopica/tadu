import subprocess
from pathlib import Path

from tadu.mutate_todo import mutate_todo
from tadu.text_hash import text_hash


def test_writes_when_hash_matches(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("a\n")
    assert mutate_todo(tmp_path, text_hash("a\n"), lambda t: t + "b\n") == "written"
    assert (tmp_path / "TODO.md").read_text() == "a\nb\n"


def test_stale_hash_writes_nothing(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("a\n")
    assert mutate_todo(tmp_path, text_hash("old\n"), lambda t: t + "b\n") == "stale"
    assert (tmp_path / "TODO.md").read_text() == "a\n"


def test_commits_only_todo(tmp_path: Path) -> None:
    def git(*args: str) -> str:
        done = subprocess.run(  # noqa: S603
            ["git", "-C", str(tmp_path), *args],  # noqa: S607
            capture_output=True, text=True, check=True,
        )  # fmt: skip
        return done.stdout

    git("init", "-q")
    git("config", "user.name", "t")
    git("config", "user.email", "t@example.com")
    (tmp_path / "TODO.md").write_text("a\n")
    git("add", "TODO.md")
    git("commit", "-qm", "init")
    (tmp_path / "other.txt").write_text("x")
    git("add", "other.txt")
    result = mutate_todo(tmp_path, text_hash("a\n"), lambda t: t + "b\n", commit_message="edit")
    assert result == "committed"
    assert git("show", "--name-only", "--format=", "HEAD").split() == ["TODO.md"]


def test_reports_commit_failed_outside_a_repository(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("a\n")
    result = mutate_todo(tmp_path, text_hash("a\n"), lambda t: t + "b\n", commit_message="edit")
    assert result == "commit-failed"
    assert (tmp_path / "TODO.md").read_text() == "a\nb\n"
