from tadu.set_field_lines import set_field_lines

LINES = ["- [ ] Fix.", "", "  Priority: high", "", "- [ ] Next.", ""]


def test_an_existing_field_is_replaced_in_place() -> None:
    assert set_field_lines(LINES, 0, "Priority", " low ")[2] == "  Priority: low"


def test_a_missing_field_ends_the_item() -> None:
    assert set_field_lines(LINES, 0, "Kind", "task") == [
        "- [ ] Fix.",
        "",
        "  Priority: high",
        "",
        "  Kind: task",
        "",
        "- [ ] Next.",
        "",
    ]


def test_a_field_of_the_next_item_is_not_touched() -> None:
    assert set_field_lines(LINES, 4, "Priority", "low")[2] == "  Priority: high"
