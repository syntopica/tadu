from dataclasses import replace

from card_samples import sample_card

from tadu.card import Card
from tadu.display_title_limit import DISPLAY_TITLE_LIMIT
from tadu.format_card_line import format_card_line


def test_line() -> None:
    expected = "shop:TODO.md:2 [backlog/decision] high T"
    assert format_card_line(sample_card()) == expected


def test_dash_without_priority() -> None:
    card = sample_card()
    bare = replace(card, item=replace(card.item, fields=replace(card.item.fields, priority=None)))
    assert format_card_line(bare) == "shop:TODO.md:2 [backlog/decision] - T"


def test_task_file_shows_due_and_its_id() -> None:
    card = sample_card()
    item = replace(card.item, path="todo/open/t-1.json", key="t-1")
    line = format_card_line(replace(card, item=item), "t-1")
    assert line == "shop:t-1 [backlog/decision] high due 2026-12-01 T"


def with_title(title: str) -> Card:
    card = sample_card()
    return replace(card, item=replace(card.item, title=title))


def test_long_title_is_cut_to_the_limit() -> None:
    line = format_card_line(with_title("x" * 200))
    title = line.removeprefix("shop:TODO.md:2 [backlog/decision] high ")
    assert title == "x" * 157 + "..."
    assert len(title) == DISPLAY_TITLE_LIMIT == 160


def test_title_at_the_limit_is_unchanged() -> None:
    assert format_card_line(with_title("x" * 160)).endswith(" " + "x" * 160)
