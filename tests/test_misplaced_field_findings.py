import re
from collections.abc import Callable

from tadu.misplaced_field_findings import misplaced_field_findings
from tadu.scan_items import scan_items


def states(marks: str) -> Callable[[re.Match[str]], bool]:
    return lambda match: match.group(1) in marks


def findings_for(lines: list[str]) -> list[tuple[int, str]]:
    (item,) = scan_items(lines, "shop", "TODO.md", states(" "))
    return [(f.line, f.message) for f in misplaced_field_findings("TODO.md", item)]


def test_no_blank_line_before_the_field() -> None:
    assert findings_for(["- [ ] A.", "  Due: 2026-11-01"]) == [
        (2, "Due is not read as a field; put a blank line before it")
    ]


def test_empty_value_is_reported_even_after_text() -> None:
    assert findings_for(["- [ ] A.", "  Due:"]) == [(2, "Due has no value")]
