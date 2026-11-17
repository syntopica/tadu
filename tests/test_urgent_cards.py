from datetime import date

from card_samples import make_card

from tadu.urgent_cards import urgent_cards

TODAY = date(2026, 11, 16)
CARDS = (
    make_card("plain"),
    make_card("normal", priority="normal"),
    make_card("high decision", kind="decision", priority="high"),
    make_card("urgent blocked", "!", "blocked", priority="urgent"),
    make_card("due tomorrow", due=date(2026, 11, 17)),
    make_card("due in two days", due=date(2026, 11, 18)),
    make_card("overdue chase", kind="waiting", due=date(2026, 11, 12)),
    make_card("urgent but done", "x", "done", priority="urgent"),
    make_card("check tomorrow", kind="later", check_on=date(2026, 11, 17)),
    make_card("urgent from next month", priority="urgent", not_before=date(2026, 12, 1)),
)


def found(days: int) -> list[tuple[str, str]]:
    return [(section, card.item.title) for section, card in urgent_cards(CARDS, TODAY, days)]


def test_priority_or_a_date_within_the_window_unless_not_started_yet() -> None:
    assert found(1) == [
        ("blocked", "urgent blocked"),
        ("decide", "high decision"),
        ("chase", "overdue chase"),
        ("do", "due tomorrow"),
        ("check", "check tomorrow"),
    ]


def test_window_of_zero_keeps_only_today_and_earlier() -> None:
    assert [title for _, title in found(0)] == ["urgent blocked", "high decision", "overdue chase"]
    assert "due in two days" in [title for _, title in found(2)]
