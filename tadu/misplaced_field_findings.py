"""F003 findings for field-like lines of one open item that are not read as fields."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.fenced_lines import fenced_lines
from tadu.field_like_pattern import FIELD_LIKE_PATTERN
from tadu.field_values import field_values
from tadu.finding import Finding

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def misplaced_field_findings(path: str, item: BacklogItem) -> list[Finding]:
    """A warning for each unfenced field-like line that field_values skips."""
    lines = item.text.splitlines()
    fenced = fenced_lines(lines)
    read = {index for index, _, _ in field_values(lines, fenced, 0, len(lines))}
    findings: list[Finding] = []
    for index in range(1, len(lines)):
        match = FIELD_LIKE_PATTERN.match(lines[index])
        if match is None or fenced[index] or index in read:
            continue
        name = match.group(1)
        empty = not lines[index].partition(":")[2].strip()
        message = (
            f"{name} has no value"
            if empty
            else f"{name} is not read as a field; put a blank line before it"
        )
        findings.append(Finding("F003", "warning", path, item.line + index, message))
    return findings
