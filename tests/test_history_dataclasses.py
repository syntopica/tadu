from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from tadu.file_versions import FileVersions
from tadu.git_commit import GitCommit
from tadu.git_file_change import GitFileChange
from tadu.history_error import HistoryError
from tadu.history_event import HistoryEvent
from tadu.history_filter import HistoryFilter
from tadu.history_lead import HistoryLead
from tadu.markdown_items import markdown_items


def test_values_are_kept_and_frozen() -> None:
    change = GitFileChange("TODO.md", ("a" * 40,), "b" * 40)
    commit = GitCommit(
        "c" * 40, "c" * 10, ("a" * 40,), "2026-11-01T09:00:00+00:00", "Ana", "S", (change,)
    )
    (item,) = markdown_items("- [ ] A.", "shop", "TODO.md")
    event = HistoryEvent(commit, None, item)
    versions = FileVersions("TODO.md", ("",), "- [ ] A.")
    lead = HistoryLead("TODO.md", "- [ ] A.", ("HEAD",))
    assert (commit.files[0].after, event.after.title, versions.before, lead.newer) == (
        "b" * 40,
        "A.",
        ("",),
        None,
    )
    for value in (change, commit, event, versions, lead):
        with pytest.raises(FrozenInstanceError):
            value.path = "x"  # type: ignore[misc,union-attr]


def test_an_empty_filter_asks_for_nothing() -> None:
    assert HistoryFilter() == HistoryFilter(frozenset(), None, None, None)
    assert HistoryFilter(since=date(2026, 11, 1)) != HistoryFilter()


def test_history_error_carries_its_message() -> None:
    assert str(HistoryError("not a git repository")) == "not a git repository"
