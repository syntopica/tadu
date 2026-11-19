from pathlib import Path

from git_repo import commit, git, git_repo
from history_repo import history_source

from tadu.blob_reader import BlobReader
from tadu.history_lead import HistoryLead
from tadu.lead_events import lead_events

ITEM = "- [ ] Ship.\n\n  Priority: low\n\n  Due: 2026-12-01\n"


def test_two_branches_and_a_lead_given_twice(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": ITEM}, "Add")
    git(root, "checkout", "-q", "-b", "bob")
    commit(root, {"TODO.md": ITEM.replace("low", "high")}, "Bob: high", "Bob")
    git(root, "checkout", "-q", "main")
    commit(root, {"TODO.md": ITEM.replace("12-01", "12-05")}, "Ana: later")
    git(root, "merge", "-q", "--no-edit", "bob", day=9)
    text = "\n".join(ITEM.replace("low", "high").replace("12-01", "12-05").splitlines())
    lead = HistoryLead("TODO.md", text, ("HEAD",))
    with BlobReader(root) as blobs:
        events = lead_events(history_source(root, blobs), [lead, lead])
    subjects = [event.commit.subject for event in events if event.commit]
    assert subjects[0].startswith("Merge branch")
    assert sorted(subjects[1:3]) == ["Ana: later", "Bob: high"]
    assert subjects[3:] == ["Add"]
