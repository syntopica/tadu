from datetime import date

import pytest

from tadu.change_days import change_days

TODAY = date(2026, 11, 18)


def test_the_last_fourteen_days_unless_given() -> None:
    assert change_days(None, None, TODAY) == (date(2026, 11, 4), TODAY)
    assert change_days(date(2026, 10, 1), None, TODAY) == (date(2026, 10, 1), TODAY)
    assert change_days(None, date(2026, 11, 10), TODAY) == (date(2026, 10, 27), date(2026, 11, 10))
    assert change_days(TODAY, TODAY, TODAY) == (TODAY, TODAY)


def test_a_first_day_after_the_last() -> None:
    with pytest.raises(ValueError, match="since 2026-11-20 is after until 2026-11-18"):
        change_days(date(2026, 11, 20), None, TODAY)
