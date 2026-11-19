from datetime import date

from history_entries import entry

from tadu.history_entry_day import history_entry_day


def test_the_commits_own_day_or_today() -> None:
    late = entry("Late", "2026-11-20T23:30:00-05:00", "Ana", [])
    assert history_entry_day(late, date(2026, 12, 1)) == "2026-11-20"
    assert history_entry_day(entry(None, None, None, []), date(2026, 12, 1)) == "2026-12-01"
