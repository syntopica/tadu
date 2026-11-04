from dataclasses import replace

from card_samples import sample_card

from tadu.format_card_line import format_card_line


def test_line() -> None:
    assert format_card_line(sample_card()) == "shop:TODO.md:2 [backlog] high T"


def test_dash_without_priority() -> None:
    card = sample_card()
    bare = replace(card, item=replace(card.item, fields=replace(card.item.fields, priority=None)))
    assert format_card_line(bare) == "shop:TODO.md:2 [backlog] - T"
