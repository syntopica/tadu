from datetime import date

from tadu.blocked_days import blocked_days


def test_days_since() -> None:
    assert blocked_days(date(2026, 11, 1), date(2026, 11, 6)) == 5


def test_unknown_and_future() -> None:
    assert blocked_days(None, date(2026, 11, 6)) is None
    assert blocked_days(date(2026, 11, 7), date(2026, 11, 6)) == 0
