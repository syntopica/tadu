from tadu.fenced_lines import fenced_lines
from tadu.field_values import field_values

LINES = [
    "- [ ] Do it.",
    "",
    "  ID: t-1",
    "",
    "  Priority: high",
    "  Due: 2026-11-20",
    "  - [ ] step",
    "",
    "    Labels: nested",
    "",
    "  ```",
    "  Queue: ready",
    "  ```",
]


def test_only_paragraph_start_unfenced_two_space_fields() -> None:
    assert field_values(LINES, fenced_lines(LINES), 0, len(LINES)) == [
        (2, "ID", "t-1"),
        (4, "Priority", "high"),
    ]


def test_end_bounds_the_scan() -> None:
    assert field_values(LINES, fenced_lines(LINES), 0, 3) == [(2, "ID", "t-1")]
