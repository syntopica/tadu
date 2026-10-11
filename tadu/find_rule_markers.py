"""Locate the rule markers that count: whole lines outside fenced code."""

from __future__ import annotations

from tadu.fence_marker import fence_marker
from tadu.rule_block_close_pattern import RULE_BLOCK_CLOSE_PATTERN
from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN
from tadu.rule_marker import RuleMarker


def find_rule_markers(text: str) -> tuple[RuleMarker, ...]:
    """Every open and close marker line, in order, skipping fenced code blocks."""
    markers: list[RuleMarker] = []
    fence: str | None = None
    start = 0
    for raw in text.split("\n"):
        end = min(start + len(raw) + 1, len(text))
        line = raw.rstrip("\r")
        run = fence_marker(line)
        if fence is not None:
            if run and run[0] == fence[0] and len(run) >= len(fence) and line.strip() == run:
                fence = None
        elif run:
            fence = run
        elif opening := RULE_BLOCK_OPEN_PATTERN.match(line):
            markers.append(RuleMarker("open", start, end, int(opening.group(1))))
        elif RULE_BLOCK_CLOSE_PATTERN.match(line):
            markers.append(RuleMarker("close", start, end, 0))
        start += len(raw) + 1
    return tuple(markers)
