"""The first paragraph of a tadu v1 item, joined into one text."""

from __future__ import annotations

from tadu.field_like_pattern import FIELD_LIKE_PATTERN
from tadu.list_marker_pattern import LIST_MARKER_PATTERN


def v1_head(text: str, lines: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    """`text` plus the wrapped lines that follow it, single-spaced, and the lines left over."""
    parts = [text.strip()]
    taken = 0
    for line in lines:
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith(("```", "~~~"))
            or LIST_MARKER_PATTERN.match(stripped)
            or FIELD_LIKE_PATTERN.match(line)
        ):
            break
        parts.append(stripped)
        taken += 1
    return " ".join(parts), lines[taken:]
