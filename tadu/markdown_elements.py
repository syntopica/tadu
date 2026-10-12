"""Split Markdown into the elements a prose-wrapping formatter must keep intact."""

from __future__ import annotations

from tadu.collapse_line import collapse_line
from tadu.element_start_pattern import ELEMENT_START_PATTERN
from tadu.fence_marker import fence_marker
from tadu.single_line_start_pattern import SINGLE_LINE_START_PATTERN


def markdown_elements(text: str) -> tuple[tuple[str, str], ...]:
    """Each element as (start prefix, text with wrapping collapsed); fenced lines stay exact."""
    elements: list[tuple[str, str]] = []
    fence: str | None = None
    joinable = False
    for raw in text.split("\n"):
        line = raw.rstrip("\r")
        run = fence_marker(line)
        if fence is not None or run:
            if fence is None:
                fence = run
            elif run and run[0] == fence[0] and len(run) >= len(fence) and line.strip() == run:
                fence = None
            elements.append(("fence", line))
            joinable = False
            continue
        if not line.strip():
            joinable = False
            continue
        start = ELEMENT_START_PATTERN.match(line)
        if joinable and start is None:
            prefix, body = elements[-1]
            elements[-1] = (prefix, body + " " + collapse_line(line))
            continue
        prefix = start.group(0).rstrip() if start else ""
        elements.append((prefix, collapse_line(line[len(start.group(0)) if start else 0 :])))
        joinable = SINGLE_LINE_START_PATTERN.match(line) is None
    return tuple(elements)
