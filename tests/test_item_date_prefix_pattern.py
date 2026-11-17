from tadu.item_date_prefix_pattern import ITEM_DATE_PREFIX_PATTERN


def test_matches_date_dash_and_bold_category() -> None:
    assert ITEM_DATE_PREFIX_PATTERN.match("2026-11-16 — **Close:** done")
    assert ITEM_DATE_PREFIX_PATTERN.match("2026-11-16 - **Close:** done")


def test_match_stops_before_the_category() -> None:
    match = ITEM_DATE_PREFIX_PATTERN.match("2026-11-16 — **Close:** done")
    assert match is not None
    assert match.end() == len("2026-11-16 — ")


def test_rejects_text_without_date_or_bold_category() -> None:
    assert not ITEM_DATE_PREFIX_PATTERN.match("**Close:** done")
    assert not ITEM_DATE_PREFIX_PATTERN.match("2026-11-16 — plain text")
