from datetime import date

from tadu.prime_briefing import prime_briefing


def test_empty_briefing_is_bounded_and_names_the_markdown_workflow() -> None:
    text = prime_briefing((), None, date(2026, 11, 24))
    assert text.startswith("Open: 0 items.")
    assert "TODO.md" in text
    assert len(text) < 2000
