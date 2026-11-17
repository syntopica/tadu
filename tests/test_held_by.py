from card_samples import make_card

from tadu.held_by import held_by


def test_unassigned_or_no_person_is_anyones() -> None:
    assert held_by(make_card("x"), "ana")
    assert held_by(make_card("x", assignees=("bo",)), None)


def test_assigned_items_are_only_their_assignees() -> None:
    shared = make_card("x", assignees=("bo", "ana"))
    assert held_by(shared, "ana")
    assert not held_by(make_card("x", assignees=("bo",)), "ana")
