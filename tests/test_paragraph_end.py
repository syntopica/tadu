from tadu.fenced_lines import fenced_lines
from tadu.paragraph_end import paragraph_end

LINES = ["  a", "  b", "", "  c", "  ```", "  d", "  ```"]


def test_blank_line_stops() -> None:
    assert paragraph_end(LINES, fenced_lines(LINES), 0, len(LINES)) == 2


def test_fence_stops() -> None:
    assert paragraph_end(LINES, fenced_lines(LINES), 3, len(LINES)) == 4


def test_end_stops() -> None:
    assert paragraph_end(LINES, fenced_lines(LINES), 0, 1) == 1
