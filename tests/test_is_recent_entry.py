from datetime import date

from tadu.is_recent_entry import is_recent_entry

CUTOFF = date(2026, 10, 15)


def test_no_day() -> None:
    assert not is_recent_entry(None, None, CUTOFF)


def test_before_marker() -> None:
    assert not is_recent_entry(date(2026, 10, 20), date(2026, 10, 25), CUTOFF)


def test_before_cutoff() -> None:
    assert not is_recent_entry(date(2026, 10, 14), None, CUTOFF)


def test_no_marker_and_recent() -> None:
    assert is_recent_entry(CUTOFF, None, CUTOFF)


def test_recent_after_marker() -> None:
    assert is_recent_entry(date(2026, 10, 20), date(2026, 10, 1), CUTOFF)
