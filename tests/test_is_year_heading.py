from tadu.is_year_heading import is_year_heading


def test_year_and_legacy_month() -> None:
    assert is_year_heading("2026")
    assert is_year_heading("2025-09")
    assert not is_year_heading("Notes")
