from datetime import date

from card_samples import make_card

from tadu.inbox_cards import inbox_cards

TODAY = date(2026, 11, 16)
SOON = date(2026, 11, 17)
CARDS = (
    make_card("task", assignees=("ana",)),
    make_card("decide", kind="decision"),
    make_card("bos call", kind="decision", assignees=("bo",)),
    make_card("decide from tomorrow", kind="decision", not_before=SOON),
    make_card("chase on its check day", kind="waiting", check_on=TODAY),
    make_card("chase past its deadline", kind="waiting", due=date(2026, 11, 10)),
    make_card("chase later", kind="waiting", check_on=SOON, due=date(2026, 11, 30)),
    make_card("chase undated", kind="waiting"),
    make_card("check overdue", kind="later", check_on=date(2026, 11, 1)),
    make_card("check undated", kind="later"),
    make_card("verify the deploy", check_on=TODAY),
    make_card("blocked, check it", "!", "blocked", check_on=TODAY),
    make_card("my blocked", "!", "blocked", assignees=("ana",)),
    make_card("loose blocked", "!", "blocked"),
    make_card("closed call", "x", "done", kind="decision"),
)


def found(person: str | None) -> list[tuple[str, str]]:
    return [(section, card.item.title) for section, card in inbox_cards(CARDS, person, TODAY)]


def test_a_person_gets_decisions_checks_that_have_come_and_their_blocked_tasks() -> None:
    assert found("ana") == [
        ("check", "check overdue"),
        ("chase", "chase past its deadline"),
        ("chase", "chase on its check day"),
        ("check", "verify the deploy"),
        ("check", "blocked, check it"),
        ("decide", "decide"),
        ("blocked", "my blocked"),
    ]


def test_without_a_person_every_decision_and_no_blocked_task() -> None:
    assert found(None) == [
        ("check", "check overdue"),
        ("chase", "chase past its deadline"),
        ("chase", "chase on its check day"),
        ("check", "verify the deploy"),
        ("check", "blocked, check it"),
        ("decide", "decide"),
        ("decide", "bos call"),
    ]
