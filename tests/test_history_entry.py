from typing import get_type_hints

from history_entries import ENTRIES

from tadu.history_change import HistoryChange
from tadu.history_entry import HistoryEntry
from tadu.history_line import HistoryLine


def test_the_keys_of_an_entry_its_changes_and_lines() -> None:
    change: HistoryChange = {"field": "state", "before": "pending", "after": "done"}
    line: HistoryLine = {"op": "+", "field": "notes", "text": "N."}
    assert set(HistoryChange.__annotations__) == set(change)
    assert set(HistoryLine.__annotations__) == set(line)
    assert set(HistoryEntry.__annotations__) == set(ENTRIES[0])
    assert get_type_hints(HistoryLine)["op"] is str
