from dataclasses import replace
from datetime import date

from card_samples import sample_card

from tadu.card import Card
from tadu.recently_done import recently_done


def card(key: str, state: str, day: date | None) -> Card:
    base = sample_card()
    return replace(base, item=replace(base.item, key=key, state=state, day=day))


def test_closed_only_newest_first_ties_keep_order() -> None:
    cards = (
        card("open", " ", date(2026, 11, 5)),
        card("old", "x", date(2026, 10, 1)),
        card("new-a", "-", date(2026, 11, 2)),
        card("blocked", "!", date(2026, 11, 4)),
        card("new-b", "x", date(2026, 11, 2)),
        card("undated", "x", None),
    )
    assert [c.item.key for c in recently_done(cards)] == ["new-a", "new-b", "old", "undated"]
