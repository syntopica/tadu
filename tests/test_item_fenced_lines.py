from tadu.fenced_lines import fenced_lines
from tadu.item_fenced_lines import item_fenced_lines


def flags(lines: list[str]) -> list[bool]:
    return item_fenced_lines(lines, fenced_lines(lines), 0, len(lines))


def test_fence_four_spaces_deep_belongs_to_the_item() -> None:
    assert flags(["- [ ] a", "    ```", "    x", "", "    ```"]) == [False, True, True, True, True]


def test_fence_six_spaces_deep_is_indented_code() -> None:
    assert flags(["- [ ] a", "", "      ```", "      x"]) == [False, False, False, False]


def test_lines_outside_the_item_keep_document_flags() -> None:
    lines = ["- [ ] a", "    ```", "- [ ] b", "```", "x", "```"]
    assert item_fenced_lines(lines, fenced_lines(lines), 0, 2) == [
        False,
        True,
        False,
        True,
        True,
        True,
    ]
