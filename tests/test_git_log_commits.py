from datetime import date
from pathlib import Path

from git_repo import commit, git_repo

from tadu.git_log_commits import git_log_commits


def test_commits_that_changed_the_paths(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    first = commit(root, {"TODO.md": "- [ ] A.\n"}, "Add A")
    commit(root, {"README.md": "hi\n"}, "Readme")
    last = commit(root, {"TODO.md": "- [ ] B.\n"}, "B instead", author="Bob")
    found = git_log_commits(root, (":(literal)TODO.md",))
    assert [(c.sha, c.author, c.date[:10]) for c in found] == [
        (last, "Bob", "2026-11-03"),
        (first, "Ana", "2026-11-01"),
    ]
    assert found[1].files[0].path == "TODO.md"
    assert found[1].files[0].before == ("0" * 40,)


def test_repository_without_commits(tmp_path: Path) -> None:
    assert git_log_commits(git_repo(tmp_path / "shop"), (":(literal)TODO.md",)) == ()


def test_since_stops_at_earlier_commits(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] A.\n"}, "One")
    commit(root, {"TODO.md": "- [ ] B.\n"}, "Two")
    commit(root, {"TODO.md": "- [ ] C.\n"}, "Three")
    found = git_log_commits(root, (":(literal)TODO.md",), since=date(2026, 11, 2))
    assert [c.subject for c in found] == ["Three", "Two"]
