"""One history entry as text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.history_header import history_header

if TYPE_CHECKING:
    from tadu.history_entry import HistoryEntry


def history_lines(entry: HistoryEntry) -> list[str]:
    """The header, then what changed: `field: before → after` (`field: value` for a new item).

    Then `+ line` and `- line` for the other lines, without the item's two-space indent, and
    `field: ` before a line of a task file's notes, done_when or evidence.
    """
    lines = [history_header(entry)]
    if entry["created"]:
        lines.append(f"  created in {entry['path']}")
    for change in entry["changes"]:
        field, old, new = change["field"], change["before"], change["after"]
        if not entry["created"]:
            lines.append(f"  {field}: {old or 'none'} → {new or 'none'}")
        elif field != "file":
            lines.append(f"  {field}: {new}")
    for line in entry["lines"]:
        text = line["text"].removeprefix("  ")
        shown = text if line["field"] == "text" else f"{line['field']}: {text}"
        lines.append(f"  {line['op']} {shown}")
    return lines if len(lines) > 1 else [*lines, "  (spacing only)"]
