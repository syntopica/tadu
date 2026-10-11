from tadu.closed_item_pattern import CLOSED_ITEM_PATTERN


def test_top_level_closed_items_match_and_open_items_do_not() -> None:
    assert CLOSED_ITEM_PATTERN.match("- [x] done")
    assert CLOSED_ITEM_PATTERN.match("- [-] dropped")
    assert not CLOSED_ITEM_PATTERN.match("- [ ] open")


def test_indented_closed_items_do_not_match() -> None:
    assert not CLOSED_ITEM_PATTERN.match("  - [x] step under a parent")
    assert not CLOSED_ITEM_PATTERN.match("  - [-] dropped step")
