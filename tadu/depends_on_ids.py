"""Task IDs named by the `Depends on:` paragraphs of one backlog item."""

from __future__ import annotations

from tadu.depends_on_line_pattern import DEPENDS_ON_LINE_PATTERN
from tadu.paragraph_end import paragraph_end
from tadu.task_id_token_pattern import TASK_ID_TOKEN_PATTERN


def depends_on_ids(lines: list[str], fenced: list[bool], first: int, end: int) -> tuple[str, ...]:
    """Each distinct ID, in order, from unfenced `Depends on:` paragraphs; other text is ignored."""
    found: list[str] = []
    for index in range(first + 1, end):
        match = DEPENDS_ON_LINE_PATTERN.match(lines[index])
        if fenced[index] or match is None or lines[index - 1].strip():
            continue
        rest = lines[index + 1 : paragraph_end(lines, fenced, index, end)]
        found.extend(TASK_ID_TOKEN_PATTERN.findall(" ".join([match.group(1), *rest])))
    return tuple(dict.fromkeys(found))
