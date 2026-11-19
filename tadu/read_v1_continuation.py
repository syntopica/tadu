"""Read the continuation lines of a tadu v1 item into its parts."""

from __future__ import annotations

import re

from tadu.file_v1_paragraph import file_v1_paragraph
from tadu.take_log_bullets import take_log_bullets
from tadu.v1_item_parts import V1ItemParts

FIELD = re.compile(r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate): (\S.*)$")


def read_v1_continuation(lines: tuple[str, ...]) -> V1ItemParts:
    """Field paragraphs, log bullets anywhere, then each remaining paragraph filed by its start.

    A field line followed only by log bullets, as `tadu close` writes an entry whose last line
    is a field, is still a field.

    Wrapping, lists and code blocks stay exactly as written: each line becomes one element.
    """
    parts = V1ItemParts()
    paragraphs: list[list[str]] = [[]]
    for line in lines:
        if line.strip():
            paragraphs[-1].append(line)
        else:
            paragraphs.append([])
    for paragraph in (p for p in paragraphs if p):
        field_match = FIELD.match(paragraph[0])
        rest = take_log_bullets(paragraph[1:] if field_match else paragraph, parts.bullets)
        if field_match and not rest:
            # keys: a repeated field line keeps the last, as the format 1 spec says
            parts.fields[field_match.group(1)] = field_match.group(2).strip()
            continue
        rest = [paragraph[0][2:], *rest] if field_match else rest
        if rest:
            file_v1_paragraph(rest, parts)
    return parts
