from pathlib import Path

from git_repo import commit, git, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.file_versions import FileVersions
from tadu.git_log_commits import git_log_commits
from tadu.versions_at import versions_at

SPECS = (":(literal)TODO.md", ":(literal)TODO_LOG.md")


def test_first_commit_changed_files_and_a_merge(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] A.\n", "TODO_LOG.md": "# Log\n"}, "Start")
    git(root, "checkout", "-q", "-b", "side")
    commit(root, {"TODO.md": "- [~] A.\n"}, "Start A")
    git(root, "checkout", "-q", "main")
    commit(root, {"TODO_LOG.md": "# Log\n\n- [x] 2026-11-02 — B.\n"}, "Log B")
    git(root, "merge", "-q", "--no-edit", "side", day=9)
    merge, log_b, start_a, start = git_log_commits(root, SPECS)
    with BlobReader(root) as blobs:
        source = history_source(root, blobs)
        assert versions_at(source, start) == (
            FileVersions("TODO.md", ("",), "- [ ] A."),
            FileVersions("TODO_LOG.md", ("",), "# Log"),
        )
        assert versions_at(source, start_a) == (FileVersions("TODO.md", ("- [ ] A.",), "- [~] A."),)
        assert [v.path for v in versions_at(source, log_b)] == ["TODO_LOG.md"]
        assert versions_at(source, merge) == (
            FileVersions("TODO.md", ("- [ ] A.", "- [~] A."), "- [~] A."),
            FileVersions(
                "TODO_LOG.md",
                ("# Log\n\n- [x] 2026-11-02 — B.", "# Log"),
                "# Log\n\n- [x] 2026-11-02 — B.",
            ),
        )
