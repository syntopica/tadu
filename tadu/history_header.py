"""The first line of one history entry."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.history_entry import HistoryEntry


def history_header(entry: HistoryEntry) -> str:
    """`<date> <time>  <short sha>  <author>  <subject>`, `  [merge]` after a merge's.

    `uncommitted  (working tree)` for the changes not yet committed.
    """
    if entry["commit"] is None:
        return "uncommitted  (working tree)"
    when = (entry["date"] or "")[:16].replace("T", " ")
    merge = "  [merge]" if entry["merge"] else ""
    return f"{when}  {entry['short']}  {entry['author']}  {entry['subject']}{merge}"
