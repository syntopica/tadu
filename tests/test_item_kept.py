from pathlib import Path

from git_repo import commit, git_repo

from tadu.blob_reader import BlobReader
from tadu.git_log_commits import git_log_commits
from tadu.item_kept import item_kept

A, B = "- [ ] A.", "- [ ] B."


def test_new_text_of_the_item_or_not(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": f"{A}\n"}, "Add A")
    commit(root, {"TODO.md": f"{A}\n{B}\n", "TODO_LOG.md": f"{A}\n"}, "Add B")
    add_b, add_a = git_log_commits(root, (":(literal)TODO.md", ":(literal)TODO_LOG.md"))
    with BlobReader(root) as blobs:
        assert item_kept(add_b, "", frozenset({("TODO.md", A)}), blobs)
        assert not item_kept(add_b, "", frozenset({("TODO.md", B)}), blobs)
        assert not item_kept(add_a, "", frozenset({("TODO.md", A)}), blobs)
        assert item_kept(add_a, "", frozenset({("TODO_LOG.md", A)}), blobs)
        assert item_kept(add_b, "", frozenset({("TODO.md", "- [ ] C.")}), blobs)
