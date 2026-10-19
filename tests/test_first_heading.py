from tadu.first_heading import first_heading

HEADINGS = [(0, 1, "T"), (2, 2, "2025"), (5, 2, "2026"), (7, 3, "2026-10")]


def test_first_accepted_heading_of_the_level_in_span() -> None:
    assert first_heading(HEADINGS, 2, range(10), lambda text: text.startswith("20")) == 2
    assert first_heading(HEADINGS, 2, range(3, 10), lambda _text: True) == 5


def test_none_when_nothing_accepts() -> None:
    assert first_heading(HEADINGS, 3, range(10), lambda text: text == "2026-11") is None
