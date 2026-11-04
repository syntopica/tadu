from tadu.fenced_lines import fenced_lines
from tadu.items_with_id import items_with_id

LINES = ["- [ ] a", "", "  ID: t-1", "- [~] b", "", "  ID: t-1", "- [x] c", "", "  ID: t-1"]


def test_only_open_items_with_that_id() -> None:
    fenced = fenced_lines(LINES)
    assert items_with_id(LINES, fenced, "t-1") == [0, 3]
    assert items_with_id(LINES, fenced, "t-2") == []
