from tadu.fenced_lines import fenced_lines
from tadu.item_id import item_id

LINES = ["- [ ] a", "", "  ID: t-1", "", "  ID: t-2", "- [ ] b", "  ID: not-a-field"]


def test_first_id_field_or_none() -> None:
    fenced = fenced_lines(LINES)
    assert item_id(LINES, fenced, 0) == "t-1"
    assert item_id(LINES, fenced, 5) is None


def test_id_inside_an_item_fence_is_not_a_field() -> None:
    lines = ["- [ ] a", "", "    ```", "", "  ID: t-9", "    ```"]
    assert item_id(lines, fenced_lines(lines), 0) is None
