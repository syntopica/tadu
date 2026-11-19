from pathlib import Path

from git_repo import commit, git, git_repo

from tadu.blob_reader import ABSENT, REMEMBERED, BlobReader


def test_reads_blobs_and_names(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"docs/TODO.md": "- [ ] A.\r\n\r\n  Note.\r\n"}, "Add")
    blob = git(root, "rev-parse", "HEAD:docs/TODO.md").strip()
    with BlobReader(root) as blobs:
        assert blobs.object_id("HEAD:docs/TODO.md") == blob
        assert blobs.object_id(blob) == blob
        assert blobs.read(blob) == "- [ ] A.\n\n  Note."
        assert blobs.read("HEAD:docs/TODO.md") == "- [ ] A.\n\n  Note."


def test_absent_unknown_and_folders_read_empty(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"docs/TODO.md": "a\n"}, "Add")
    with BlobReader(root) as blobs:
        assert blobs.object_id("HEAD:docs/gone blob.md") == ABSENT
        assert blobs.object_id("HEAD:docs") == ABSENT
        assert blobs.read("HEAD:docs/gone.md") == ""
        assert blobs.read(ABSENT) == ""
        assert blobs.read("1" * 40) == ""


def test_recent_texts_are_kept_and_old_ones_dropped(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {f"{n}.md": f"{n}\n" for n in range(REMEMBERED + 1)}, "Add")
    with BlobReader(root) as blobs:
        texts = [blobs.read(f"HEAD:{n}.md") for n in range(REMEMBERED + 1)]
        assert texts == [str(n) for n in range(REMEMBERED + 1)]
        assert blobs.read(f"HEAD:{REMEMBERED}.md") == str(REMEMBERED)
        assert blobs.read("HEAD:0.md") == "0"
