from datetime import date

from card_samples import make_card

from tadu.attention_order import attention_order
from tadu.open_cards import open_cards


def test_order_is_priority_then_date_then_column() -> None:
    assert attention_order(make_card("x", priority="high")) == (1, date.max, 2)
    assert attention_order(make_card("x", due=date(2026, 1, 2))) == (4, date(2026, 1, 2), 2)
    assert attention_order(make_card("x", "~", "in_progress")) == (4, date.max, 0)
    assert attention_order(make_card("x", "!", "blocked")) == (4, date.max, 3)
    both = make_card("x", due=date(2026, 1, 9), check_on=date(2026, 1, 2))
    assert attention_order(both) == (4, date(2026, 1, 2), 2)


def test_closed_cards_leave_and_ties_keep_read_order() -> None:
    cards = (
        make_card("plain-1"),
        make_card("done", "x", "done", priority="urgent"),
        make_card("cancelled", "-", "cancelled"),
        make_card("plain-2"),
        make_card("dated", due=date(2026, 11, 20)),
        make_card("ready", column="ready"),
        make_card("low", priority="low"),
        make_card("urgent", priority="urgent"),
    )
    assert [card.item.title for card in open_cards(cards)] == [
        *("urgent", "low", "dated", "ready", "plain-1", "plain-2"),
    ]
