from datetime import date
from pathlib import Path

from changes_repo import changes_repo
from git_repo import commit, git_repo

from tadu.backlog_changes import backlog_changes
from tadu.change_repository import ChangeRepository


def test_repositories_newest_first_and_problems(tmp_path: Path) -> None:
    shop = changes_repo(tmp_path / "shop")
    web = git_repo(tmp_path / "web")
    commit(web, {"TODO.md": "- [ ] Web.\n"}, "One")
    commit(web, {"TODO.md": "- [ ] Web.\n- [ ] Later.\n"}, "Two")
    commit(web, {"TODO.md": "- [ ] Web.\n- [ ] Later.\n- [ ] Latest.\n"}, "Three")
    commit(web, {"TODO.md": "- [~] Web.\n- [ ] Later.\n- [ ] Latest.\n"}, "Four")
    repositories = (
        ChangeRepository("shop", None, shop),
        ChangeRepository("plain", None, tmp_path),
        ChangeRepository("web", None, web),
    )
    entries, problems = backlog_changes(repositories, date(2026, 11, 3), date(2026, 11, 4))
    assert [
        (entry["repository"], (entry["date"] or "")[:10], entry["event"]) for entry in entries
    ] == [
        ("shop", "2026-11-04", "blocked"),
        ("web", "2026-11-04", "started"),
        ("shop", "2026-11-03", "started"),
        ("web", "2026-11-03", "created"),
    ]
    assert [problem.repository for problem in problems] == ["plain"]
    assert problems[0].message.startswith("not a git repository")
