"""File one paragraph of a tadu v1 item under the right part."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tadu.task_id_pattern import TASK_ID_PATTERN

if TYPE_CHECKING:
    from tadu.v1_item_parts import V1ItemParts

ID_TEXT = re.compile(TASK_ID_PATTERN.pattern.strip("^$"))


def file_v1_paragraph(lines: list[str], parts: V1ItemParts) -> None:
    """`Depends on:` with task ids -> blocked_by, `Done when:` -> done_when, anything else -> notes."""
    text = " ".join(lines)
    if text.startswith("Depends on:") and ID_TEXT.search(text):
        parts.blocked_by += ID_TEXT.findall(text)
    elif lines[0].startswith("Done when:"):
        first = lines[0][len("Done when:") :].strip()
        parts.done_when += (
            ([""] if parts.done_when else []) + ([first] if first else []) + lines[1:]
        )
    else:
        parts.notes += ([""] if parts.notes else []) + lines
