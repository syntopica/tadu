from datetime import date

from history_entries import ENTRIES

from tadu.change_entry import ChangeEntry
from tadu.filter_changes import filter_changes
from tadu.history_filter import HistoryFilter

EVENTS = ["changed", "closed", "started", "changed", "created"]
CHANGES = [
    ChangeEntry(**entry, repository="shop", project=None, key=None, title="T", event=event)
    for entry, event in zip(ENTRIES, EVENTS, strict=True)
]
TODAY = date(2026, 11, 25)


def test_events_then_the_history_filter() -> None:
    assert filter_changes(CHANGES, HistoryFilter(), frozenset(), TODAY) == CHANGES
    closed = filter_changes(CHANGES, HistoryFilter(), frozenset({"closed", "started"}), TODAY)
    assert [entry["subject"] for entry in closed] == ["Close it", "Take it"]
    narrowed = filter_changes(
        CHANGES, HistoryFilter(frozenset({"state"})), frozenset({"started"}), TODAY
    )
    assert [change["field"] for change in narrowed[0]["changes"]] == ["state"]
    assert narrowed[0]["event"] == "started"
