from tadu.section_counts import section_counts
from tadu.section_titles import SECTION_TITLES


def test_counts_in_section_order_nonzero_only() -> None:
    sections = ["blocked", "decide", "check", "decide", "do"]
    assert section_counts(sections) == "1 to do, 2 to decide, 1 to check, 1 blocked"
    assert section_counts([]) == ""


def test_every_section_has_a_title_saying_who_acts() -> None:
    assert list(SECTION_TITLES) == ["do", "decide", "chase", "check", "blocked"]
    assert SECTION_TITLES["decide"] == "Decide: choices a person must make"
