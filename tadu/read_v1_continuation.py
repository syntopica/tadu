"""Read the continuation lines of a tadu v1 item into its parts."""

from __future__ import annotations

import re

from tadu.file_v1_paragraph import file_v1_paragraph
from tadu.take_log_bullets import take_log_bullets
from tadu.v1_item_parts import V1ItemParts

FIELD = re.compile(
    r"^  (ID|Priority|Assignees|Due|Labels|Queue|Kind|Check on|Not before|Estimate): (\S.*)$"
)


def read_v1_continuation(lines: tuple[str, ...]) -> V1ItemParts:
    """Field lines, log bullets anywhere, then each remaining paragraph filed by its start.

    A field line is one that starts a paragraph after a blank line, as doctor and list read
    it, whatever follows it there: `tadu close` writes an entry's `ID:` right above its
    `- Evidence:`. A lone field line right under the item's first line counts too. Only the
    first line of a name is a field, as the format 1 spec says; a repeat stays text, after a
    line repeating the first, so the notes show every value given. Wrapping,
    lists and code blocks stay exactly as written: each line becomes one element.
    """
    parts = V1ItemParts()
    paragraphs: list[list[str]] = [[]]
    for line in lines:
        if line.strip():
            paragraphs[-1].append(line)
        else:
            paragraphs.append([])
    for number, paragraph in enumerate(paragraphs):
        field_match = FIELD.match(paragraph[0]) if paragraph else None
        read = (
            field_match is not None
            and (number > 0 or len(paragraph) == 1)
            and field_match.group(1) not in parts.fields
        )
        if field_match and read:
            # keys: set only for a name not read yet; a repeated line stays text
            parts.fields[field_match.group(1)] = field_match.group(2).strip()
        elif field_match and field_match.group(1) in parts.fields:
            # a repeat: the notes show every value given, the first (the field) included
            first = f"{field_match.group(1)}: {parts.fields[field_match.group(1)]}"
            parts.notes += [] if first in parts.notes else [*([""] if parts.notes else []), first]
        rest = take_log_bullets(paragraph[1:] if read else paragraph, parts.bullets)
        if rest:
            file_v1_paragraph(rest, parts)
    return parts
