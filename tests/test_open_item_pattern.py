from tadu.open_item_pattern import OPEN_ITEM_PATTERN


def test_open_states_match() -> None:
    assert all(OPEN_ITEM_PATTERN.match(f"- [{s}] a") for s in (" ", "~", "!"))


def test_closed_and_nested_items_do_not_match() -> None:
    assert not OPEN_ITEM_PATTERN.match("- [x] a")
    assert not OPEN_ITEM_PATTERN.match("  - [ ] a")
