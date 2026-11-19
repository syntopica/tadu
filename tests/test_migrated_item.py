from pathlib import Path

from git_repo import commit, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.migrated_item import migrated_item
from tadu.stable_task_id import stable_task_id

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def test_by_id_by_derived_id_or_none(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    sha = commit(
        root,
        {
            "app/TODO.md": "# TODO\n\n- [ ] Open one.\n",
            "app/TODO_LOG.md": "# TODO Log\n",
            "app/docs/todo-log/2025.md": f"- [x] 2025-01-02 — Archived.\n\n  ID: {ID}\n  - Evidence: e.\n"
            "- [x] 2025-01-03 — Derived.\n  - Evidence: e.\n",
        },
        "Backlog",
    )
    derived = stable_task_id("docs/todo-log/2025.md:1", "Derived.")
    with BlobReader(root) as blobs:
        source = history_source(root, blobs)
        found = migrated_item(source, sha, "app", ID)
        assert found is not None
        assert (found.path, found.title) == ("app/docs/todo-log/2025.md", "Archived.")
        found = migrated_item(source, sha, "app", derived)
        assert found is not None
        assert (found.path, found.title) == ("app/docs/todo-log/2025.md", "Derived.")
        assert migrated_item(source, sha, "app", "t-00000000-0000-4000-8000-000000000000") is None
        assert migrated_item(source, sha, "elsewhere", ID) is None


def test_an_empty_todo_still_has_a_log(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    log = f"- [x] 2025-01-02 — Logged.\n\n  ID: {ID}\n  - Evidence: e.\n"
    sha = commit(root, {"TODO.md": "\n", "TODO_LOG.md": log}, "Backlog")
    with BlobReader(root) as blobs:
        found = migrated_item(history_source(root, blobs), sha, ".", ID)
    assert found is not None
    assert found.path == "TODO_LOG.md"
