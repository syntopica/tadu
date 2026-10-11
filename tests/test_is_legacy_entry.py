from datetime import date

from tadu.is_legacy_entry import is_legacy_entry


def test_before_since_is_legacy() -> None:
    since = date(2026, 10, 1)
    assert is_legacy_entry("2026-09-30", since)
    assert not is_legacy_entry("2026-10-01", since)
    assert not is_legacy_entry("2026-13-45", since)
