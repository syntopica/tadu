from tadu.holds_item_text import holds_item_text

TEXT = "# TODO\n\n- [ ] A.\n\n  Note.\n- [ ] B.\n- [ ] A."


def test_whole_items() -> None:
    assert holds_item_text(TEXT, "- [ ] A.\n\n  Note.")
    assert holds_item_text(TEXT, "- [ ] B.")


def test_a_later_occurrence_counts() -> None:
    assert holds_item_text(TEXT, "- [ ] A.")


def test_part_of_an_item_is_not_the_item() -> None:
    assert not holds_item_text(TEXT, "- [ ] A.\n\n  Not")
    assert not holds_item_text("x - [ ] B.", "- [ ] B.")
    assert not holds_item_text(TEXT, "- [ ] C.")
