from datetime import date

from tadu.iso_date import iso_date


def test_formats_and_none() -> None:
    assert iso_date(date(2026, 11, 4)) == "2026-11-04"
    assert iso_date(None) is None
