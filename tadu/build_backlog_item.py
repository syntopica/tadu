"""Build one backlog item from its first line."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.backlog_item import BacklogItem
from tadu.field_values import field_values
from tadu.item_span_end import item_span_end
from tadu.parse_item_day import parse_item_day
from tadu.parse_item_fields import parse_item_fields

if TYPE_CHECKING:
    import re


def build_backlog_item(
    lines: list[str],
    fenced: list[bool],
    match: re.Match[str],
    at: tuple[int, str, str, str],
) -> BacklogItem:
    """The item whose first line matched; at is (first index, path, derived key, title)."""
    first, path, fallback_key, title = at
    end = item_span_end(lines, first)
    fields, problems = parse_item_fields(field_values(lines, fenced, first, end))
    return BacklogItem(
        key=fields.id or fallback_key,
        stable=fields.id is not None,
        path=path,
        line=first + 1,
        end_line=end,
        state=match.group(1),
        day=parse_item_day(match.group(2)),
        title=title,
        text="\n".join(lines[first:end]),
        fields=fields,
        problems=problems,
    )
