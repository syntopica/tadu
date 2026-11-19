from pathlib import Path

from git_repo import commit, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.first_change import first_change
from tadu.history_lead import HistoryLead


def test_lines_dropped_from_the_end(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] Ship.\n\n  Priority: high\n"}, "Add")
    dropped = commit(root, {"TODO.md": "- [ ] Ship.\n"}, "Drop priority")
    commit(root, {"TODO.md": "- [ ] Other.\n- [ ] Ship.\n"}, "Add other")
    with BlobReader(root) as blobs:
        source = history_source(root, blobs)
        found = first_change(source, HistoryLead("TODO.md", "- [ ] Ship.", ("HEAD",)))
        assert found is not None
        assert found.sha == dropped
        assert first_change(source, HistoryLead("TODO.md", "- [ ] Never.", ("HEAD",))) is None
