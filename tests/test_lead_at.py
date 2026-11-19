from pathlib import Path

from git_repo import commit, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.git_log_commits import git_log_commits
from tadu.history_lead import HistoryLead
from tadu.lead_at import lead_at

SPECS = (":(literal)TODO.md", ":(literal)TODO_LOG.md")


def test_change_creation_and_a_parent_that_held_it(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] A.\n"}, "Add A")
    commit(root, {"TODO.md": "- [~] A.\n"}, "Start A")
    commit(root, {"TODO.md": "- [~] A.\n- [ ] B.\n"}, "Add B")
    add_b, start_a, add_a = git_log_commits(root, SPECS)
    with BlobReader(root) as blobs:
        source = history_source(root, blobs)
        lead = HistoryLead("TODO.md", "- [~] A.", ("HEAD",), "newer")
        assert lead_at(source, add_b, lead) == (
            None,
            (HistoryLead("TODO.md", "- [~] A.", (start_a.sha,), "newer"),),
        )
        event, leads = lead_at(source, start_a, lead)
        assert event is not None
        assert event.before is not None
        assert (event.commit, event.before.text, event.after.text) == (
            start_a,
            "- [ ] A.",
            "- [~] A.",
        )
        assert leads == (HistoryLead("TODO.md", "- [ ] A.", (add_a.sha,), start_a.sha),)
        event, leads = lead_at(source, add_a, HistoryLead("TODO.md", "- [ ] A.", ("HEAD",)))
        assert event is not None
        assert (event.before, leads) == (None, ())


def test_text_that_is_no_item(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "Plain words.\n"}, "Add")
    (added,) = git_log_commits(root, SPECS)
    with BlobReader(root) as blobs:
        lead = HistoryLead("TODO.md", "Plain words.", ("HEAD",))
        assert lead_at(history_source(root, blobs), added, lead) == (None, ())
