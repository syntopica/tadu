from dataclasses import replace

from card_samples import sample_card

from tadu.card import Card
from tadu.card_json import card_json

KEYS = [
    *("key", "stable", "repository", "path", "line", "end_line", "state", "column"),
    *("title", "text", "day", "priority", "assignees", "due", "labels", "queue"),
    *("estimate", "project", "organizations", "problems", "editor_url", "remote_url"),
]


def test_keys() -> None:
    assert list(card_json(sample_card())) == KEYS


def test_values() -> None:
    data = card_json(sample_card())
    assert data["problems"] == [{"line": 5, "message": "bad"}]
    assert data["organizations"] == [{"role": "client", "org": "acme"}]
    assert (data["day"], data["due"]) == ("2026-11-01", "2026-12-01")
    assert (data["assignees"], data["labels"]) == (["ana"], ["x"])
    assert data["text"] == "<b>T</b>"


def test_absent_dates_are_null() -> None:
    card = sample_card()
    item = replace(card.item, day=None, fields=replace(card.item.fields, due=None))
    data = card_json(Card(item, "shop", "backlog", None, (), None, None))
    assert (data["day"], data["due"], data["project"]) == (None, None, None)
