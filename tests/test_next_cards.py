from datetime import date

from card_samples import make_card

from tadu.next_cards import next_cards

TODAY = date(2026, 11, 16)
CARDS = (
    make_card("mine", assignees=("ana",)),
    make_card("bos", assignees=("bo",)),
    make_card("started", "~", "in_progress"),
    make_card("blocked", "!", "blocked"),
    make_card("decision", kind="decision"),
    make_card("waiting", kind="waiting"),
    make_card("later", kind="later"),
    make_card("urgent", priority="urgent"),
    make_card("a task", kind="task", priority="high"),
    make_card("from tomorrow", not_before=date(2026, 11, 17)),
    make_card("from today", not_before=TODAY),
    make_card("done", "x", "done"),
)


def titles(person: str | None) -> list[str]:
    return [card.item.title for card in next_cards(CARDS, person, TODAY)]


def test_tasks_and_unclassified_items_that_can_go_on_most_pressing_first() -> None:
    assert titles(None) == ["urgent", "a task", "started", "mine", "bos", "from today"]


def test_a_person_drops_what_is_assigned_only_to_others() -> None:
    assert titles("ana") == ["urgent", "a task", "started", "mine", "from today"]
