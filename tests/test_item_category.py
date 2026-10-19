from tadu.item_category import item_category

HEADINGS = [(0, 1, "TODO"), (2, 2, "Frontend"), (5, 3, "Sub"), (8, 2, ""), (10, 2, "Ops")]


def test_nearest_non_empty_heading_of_the_level_above() -> None:
    assert item_category(HEADINGS, 6, 2) == "Frontend"
    assert item_category(HEADINGS, 9, 2) == "Frontend"
    assert item_category(HEADINGS, 11, 2) == "Ops"


def test_none_above_the_first_section() -> None:
    assert item_category(HEADINGS, 1, 2) is None
