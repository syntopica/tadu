from pathlib import Path

import pytest
from git_repo import commit, git_repo
from history_repo import history_source

import tadu.follow_lead as follow_lead_module
from tadu.blob_reader import BlobReader
from tadu.follow_lead import follow_lead
from tadu.history_lead import HistoryLead


def test_pickaxe_fallback_and_nothing(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    added = commit(root, {"TODO.md": "- [ ] Ship.\n\n  Priority: high\n"}, "Add")
    dropped = commit(root, {"TODO.md": "- [ ] Ship.\n"}, "Drop priority")
    with BlobReader(root) as blobs:
        source = history_source(root, blobs)
        event, leads = follow_lead(source, HistoryLead("TODO.md", "- [ ] Ship.", ("HEAD",)))
        assert event is not None
        assert event.commit is not None
        assert event.commit.sha == dropped
        assert leads == (
            HistoryLead("TODO.md", "- [ ] Ship.\n\n  Priority: high", (added,), dropped),
        )
        assert follow_lead(source, HistoryLead("TODO.md", "- [ ] Gone.", ("HEAD",))) == (None, ())


def test_text_found_only_inside_another_item(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] Ship.\n\n  Priority: high\n"}, "Add")
    with BlobReader(root) as blobs:
        lead = HistoryLead("TODO.md", "- [ ] Ship.", ("HEAD",))
        assert follow_lead(history_source(root, blobs), lead) == (None, ())


def test_an_item_too_long_to_search_for(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = git_repo(tmp_path / "shop")
    added = commit(root, {"TODO.md": "- [ ] Ship.\n"}, "Add")
    monkeypatch.setattr(follow_lead_module, "MAX_SEARCH_BYTES", 5)
    with BlobReader(root) as blobs:
        event, _ = follow_lead(
            history_source(root, blobs), HistoryLead("TODO.md", "- [ ] Ship.", ("HEAD",))
        )
    assert event is not None
    assert event.commit is not None
    assert event.commit.sha == added
