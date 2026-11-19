from pathlib import Path

from git_repo import commit, git_repo

from tadu.pickaxe_commit import pickaxe_commit

SPEC = (":(literal)TODO.md",)


def test_newest_commit_that_changed_the_count(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    added = commit(root, {"TODO.md": "- [ ] A.\n"}, "Add A")
    commit(root, {"TODO.md": "- [ ] A.\n- [ ] B.\n"}, "Add B")
    found = pickaxe_commit(root, "- [ ] A.", ("HEAD",), SPEC)
    assert found is not None
    assert (found.sha, found.subject, found.files) == (added, "Add A", ())
    assert pickaxe_commit(root, "- [ ] A.", (f"{added}^",), SPEC) is None
    assert pickaxe_commit(root, "-n5", ("HEAD",), SPEC) is None
