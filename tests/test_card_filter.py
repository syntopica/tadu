from datetime import date

from tadu.card_filter import CardFilter


def test_defaults_set_nothing() -> None:
    card_filter = CardFilter()
    assert card_filter.project is None
    assert card_filter.due_before is None
    assert card_filter.include_cancelled is False


def test_holds_values() -> None:
    card_filter = CardFilter(org="acme", role="client", due_before=date(2026, 1, 1))
    assert (card_filter.org, card_filter.role) == ("acme", "client")
