from dataclasses import replace
from datetime import date

from card_samples import sample_card

from tadu.card import Card
from tadu.card_json import card_json

TODAY = date(2026, 11, 6)

KEYS = [
    *("key", "stable", "repository", "path", "line", "end_line", "state", "column"),
    *("title", "text", "day", "priority", "assignees", "due", "labels", "queue"),
    *("estimate", "project", "organizations", "problems", "editor_url", "remote_url"),
    *("blocked_since", "blocked_days"),
]


def test_keys() -> None:
    assert list(card_json(sample_card(), TODAY)) == KEYS


def test_values() -> None:
    data = card_json(sample_card(), TODAY)
    assert data["problems"] == [{"line": 5, "message": "bad"}]
    assert data["organizations"] == [{"role": "client", "org": "acme"}]
    assert (data["day"], data["due"]) == ("2026-11-01", "2026-12-01")
    assert (data["assignees"], data["labels"]) == (["ana"], ["x"])
    assert data["text"] == "<b>T</b>"


def test_absent_dates_are_null() -> None:
    card = sample_card()
    item = replace(card.item, day=None, fields=replace(card.item.fields, due=None))
    data = card_json(Card(item, "shop", "backlog", None, (), None, None), TODAY)
    assert (data["day"], data["due"], data["project"]) == (None, None, None)
    assert (data["blocked_since"], data["blocked_days"]) == (None, None)


def test_blocked_age() -> None:
    card = replace(sample_card(), blocked_since=date(2026, 11, 1))
    data = card_json(card, TODAY)
    assert (data["blocked_since"], data["blocked_days"]) == ("2026-11-01", 5)
