from tadu.log_entry_pattern import LOG_ENTRY_PATTERN


def test_dated_closed_entries_match() -> None:
    assert LOG_ENTRY_PATTERN.match("- [x] 2026-10-01 — **Backend:** Fixed.")
    assert not LOG_ENTRY_PATTERN.match("- [x] Fixed without a date.")
