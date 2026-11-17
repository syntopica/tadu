from tadu.insert_item import insert_item

ITEM = ["- [ ] New."]
TEXT = [
    "# TODO",
    "",
    "## Billing",
    "",
    "- [ ] Old.",
    "",
    "### Notes",
    "",
    "- [ ] Deeper.",
    "",
    "## Shipping",
    "",
    "- [ ] Ship.",
    "",
]


def test_last_in_its_section_before_the_next_one() -> None:
    lines, index = insert_item(TEXT, ITEM, "Billing")
    assert lines[8:13] == ["- [ ] Deeper.", "", "- [ ] New.", "", "## Shipping"]
    assert index == 10


def test_last_section_and_no_category_go_to_the_end() -> None:
    for category in ("Shipping", None):
        lines, index = insert_item(TEXT, ITEM, category)
        assert lines[-4:] == ["- [ ] Ship.", "", "- [ ] New.", ""]
        assert index == len(lines) - 2


def test_a_new_category_gets_its_heading_at_the_end() -> None:
    lines, index = insert_item(["# TODO"], ITEM, "Ops")
    assert lines == ["# TODO", "", "## Ops", "", "- [ ] New.", ""]
    assert index == 4


def test_a_heading_inside_a_fence_is_not_a_section() -> None:
    lines, _ = insert_item(["```", "## Ops", "```"], ITEM, "Ops")
    assert lines[-4:] == ["## Ops", "", "- [ ] New.", ""]


def test_empty_file() -> None:
    assert insert_item([""], ITEM, None) == (["- [ ] New.", ""], 0)
