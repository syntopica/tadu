from pathlib import Path

from git_repo import commit, git_repo

from tadu.blob_reader import BlobReader
from tadu.change_source import ChangeSource
from tadu.file_versions import FileVersions
from tadu.git_log_commits import git_log_commits
from tadu.markdown_commit_versions import markdown_commit_versions


def test_the_backlog_files_a_commit_changed(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "shop")
    files = {
        "app/docs/TODO.md": "- [ ] A.\n",
        "app/docs/TODO_LOG.md": "# Log\n",
        "app/docs/docs/todo-log/2025.md": "- [x] 2025-01-01 — Old.\n",
        "app/docs/docs/todo-log/notes.md": "x\n",
        "app/docs/README.md": "hi\n",
        "app/TODO.md": "- [ ] Elsewhere.\n",
    }
    commit(repo, files, "Start")
    (only,) = git_log_commits(repo / "app", (".",))
    with BlobReader(repo / "app") as blobs:
        source = ChangeSource("shop", None, repo / "app", "app/", "docs", blobs)
        assert markdown_commit_versions(source, only) == (
            FileVersions("docs/TODO.md", ("",), "- [ ] A."),
            FileVersions("docs/TODO_LOG.md", ("",), "# Log"),
            FileVersions("docs/docs/todo-log/2025.md", ("",), "- [x] 2025-01-01 — Old."),
        )
