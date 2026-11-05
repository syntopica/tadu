from datetime import UTC, datetime

from tadu.local_date import local_date


def test_matches_local_calendar() -> None:
    stamp = 1_700_000_000
    assert local_date(stamp) == datetime.fromtimestamp(stamp, UTC).astimezone().date()
