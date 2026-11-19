from datetime import date

from history_entries import ENTRIES

from tadu.filter_history import filter_history
from tadu.history_filter import HistoryFilter

TODAY = date(2026, 11, 25)


def subjects(wanted: HistoryFilter) -> list[str | None]:
    return [entry["subject"] for entry in filter_history(ENTRIES, wanted, TODAY)]


def test_no_filter_keeps_everything() -> None:
    assert filter_history(ENTRIES, HistoryFilter(), TODAY) == ENTRIES


def test_fields_keep_only_their_changes() -> None:
    kept = filter_history(ENTRIES, HistoryFilter(frozenset({"state", "assignees"})), TODAY)
    assert [entry["subject"] for entry in kept] == ["Close it", "Take it", "Add it"]
    assert [change["field"] for change in kept[1]["changes"]] == ["assignees", "state"]
    assert [change["field"] for change in kept[0]["changes"]] == ["state"]
    assert kept[0]["lines"] == []
    assert ENTRIES[1]["lines"] != []


def test_line_fields() -> None:
    assert subjects(HistoryFilter(frozenset({"notes"}))) == ["Note it"]
    assert subjects(HistoryFilter(frozenset({"text"}))) == ["Close it"]


def test_days_are_inclusive_and_the_commits_own() -> None:
    assert subjects(HistoryFilter(since=date(2026, 11, 10))) == [None, "Close it", "Take it"]
    assert subjects(HistoryFilter(until=date(2026, 11, 10))) == ["Take it", "Note it", "Add it"]
    # 23:30 at -05:00 is the 20th where it was committed, though the 21st in UTC
    assert subjects(HistoryFilter(since=date(2026, 11, 20), until=date(2026, 11, 20))) == [
        "Close it"
    ]
    assert subjects(HistoryFilter(until=date(2026, 11, 24))) == [
        "Close it",
        "Take it",
        "Note it",
        "Add it",
    ]


def test_author_is_a_part_of_the_name_in_any_case() -> None:
    assert subjects(HistoryFilter(author="BOB")) == ["Take it", "Note it"]
    assert subjects(HistoryFilter(author="díaz")) == ["Close it", "Add it"]


def test_all_together() -> None:
    wanted = HistoryFilter(frozenset({"state"}), date(2026, 11, 2), None, "ana")
    assert subjects(wanted) == ["Close it"]
