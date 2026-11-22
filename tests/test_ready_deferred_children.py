from dataclasses import replace
from datetime import date, timedelta

from card_samples import make_card

from tadu.card import Card
from tadu.ready_cards import ready_cards
from tadu.task_extras import TaskExtras

TODAY = date(2026, 11, 22)


def card(key: str, **extras: object) -> Card:
    made = make_card(key)
    return replace(made, item=replace(made.item, extras=TaskExtras(**extras)))  # type: ignore[arg-type]


def keys(cards: tuple[Card, ...]) -> list[str]:
    return sorted(c.item.key for c in cards)


def test_children_of_a_deferred_parent_wait_with_it_at_any_depth() -> None:
    cards = (
        card("parent", defer_until=TODAY + timedelta(days=3)),
        card("child", relations=(("parent", "parent"),)),
        card("grandchild", relations=(("parent", "child"),)),
        card("free"),
    )
    assert keys(ready_cards(cards, TODAY)) == ["free"]
    assert keys(ready_cards(cards, TODAY, with_deferred_children=True)) == [
        "child",
        "free",
        "grandchild",
    ]


def test_children_of_a_parent_whose_day_has_come_are_ready() -> None:
    cards = (card("parent", defer_until=TODAY), card("child", relations=(("parent", "parent"),)))
    assert keys(ready_cards(cards, TODAY)) == ["child", "parent"]


def test_a_parent_cycle_does_not_loop() -> None:
    cards = (card("a", relations=(("parent", "b"),)), card("b", relations=(("parent", "a"),)))
    assert keys(ready_cards(cards, TODAY)) == ["a", "b"]
