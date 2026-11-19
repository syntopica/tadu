from pathlib import Path

from git_repo import commit, git_repo

from tadu.git_log_commits import git_log_commits
from tadu.migration_commit import migration_commit


def test_todo_md_removed_and_tadu_json_added(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "shop")
    commit(repo, {"app/TODO.md": "- [ ] A.\n"}, "Start")
    commit(repo, {"app/TODO.md": "", "app/todo/tadu.json": "{}\n"}, "Migrate")
    commit(repo, {"app/todo/tadu.json": "{ }\n"}, "Edit the config")
    commit(repo, {"app/TODO.md": "- [ ] B.\n"}, "A new TODO.md")
    commit(repo, {"app/TODO.md": ""}, "Remove it")
    remove, again, edit, migrate, start = git_log_commits(repo, ("app",))
    assert [migration_commit(c, "", "app") for c in (remove, again, edit, migrate, start)] == [
        False,
        False,
        False,
        True,
        False,
    ]
    assert migration_commit(migrate, "app/", ".")
    assert not migration_commit(migrate, "", ".")
