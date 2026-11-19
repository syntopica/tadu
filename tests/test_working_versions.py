from pathlib import Path

from git_repo import commit, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.file_versions import FileVersions
from tadu.working_versions import working_versions


def test_changed_files_only_in_a_subdirectory(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "shop")
    commit(repo, {"app/TODO.md": "- [ ] A.\n", "app/TODO_LOG.md": "# Log\n"}, "Add A")
    root = repo / "app"
    with BlobReader(root) as blobs:
        source = history_source(root, blobs, "app/")
        assert working_versions(source) == ()
        (root / "TODO.md").write_text("- [~] A.\n")
        assert working_versions(source) == (FileVersions("TODO.md", ("- [ ] A.",), "- [~] A."),)
