from tadu.fenced_lines import fenced_lines
from tadu.item_title import item_title


def title_of(lines: list[str]) -> str:
    return item_title(lines, fenced_lines(lines), 0, lines[0][6:])


def test_wrapped_title_is_joined() -> None:
    lines = ["- [ ] Fix the shop", "  checkout flow", "\t and the cart."]
    assert title_of(lines) == "Fix the shop checkout flow and the cart."


def test_single_line_title_is_unchanged() -> None:
    assert title_of(["- [ ] Fix it.", "", "  Priority: high"]) == "Fix it."


def test_stops_at_blank_line() -> None:
    assert title_of(["- [ ] One", "  two", "", "  three"]) == "One two"


def test_stops_at_nested_list_items() -> None:
    for marker in ("- ", "* ", "+ ", "1. ", "12) "):
        assert title_of(["- [ ] One", f"  {marker}[ ] step"]) == "One"


def test_stops_at_a_field_like_line() -> None:
    assert title_of(["- [ ] One", "  two", "  Priority: high"]) == "One two"
    assert title_of(["- [ ] One", "  Due:"]) == "One"


def test_stops_at_a_fence() -> None:
    assert title_of(["- [ ] One", "  two", "  ```", "  code", "  ```"]) == "One two"


def test_stops_at_unindented_line() -> None:
    assert title_of(["- [ ] One", "next"]) == "One"


def test_carriage_returns_are_dropped() -> None:
    assert title_of(["- [ ] One\r", "  two\r"]) == "One two"


def test_log_entry_title_stops_at_nested_evidence() -> None:
    lines = ["- [x] 2026-10-20 — **A:** wrapped", "  title.", "  - Evidence: ok"]
    assert item_title(lines, fenced_lines(lines), 0, "**A:** wrapped") == "**A:** wrapped title."
