"""One change as a line of `tadu changes`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.display_title_limit import DISPLAY_TITLE_LIMIT
from tadu.line_facts import line_facts

if TYPE_CHECKING:
    from tadu.change_entry import ChangeEntry


def change_line(entry: ChangeEntry, key: str | None) -> str:
    """`  <day>  <author>  <repository>:<key or file>  <title>`, then what changed.

    `key` is the short key to show, None for an item without one. A reopened item shows how its
    state went; a changed one, its fields (all but `file`), then how many lines of each field it
    added and removed.
    """
    title = entry["title"]
    if len(title) > DISPLAY_TITLE_LIMIT:
        title = title[: DISPLAY_TITLE_LIMIT - 3] + "..."
    where = f"{entry['repository']}:{key or entry['path']}"
    line = f"  {(entry['date'] or '')[:10]}  {entry['author']}  {where}  {title}"
    shown = {"reopened": ("state",), "changed": None}.get(entry["event"], ())
    facts = [
        f"{change['field']}: {change['before'] or 'none'} → {change['after'] or 'none'}"
        for change in entry["changes"]
        if change["field"] != "file" and (shown is None or change["field"] in shown)
    ]
    if shown is None:
        facts += line_facts(entry["lines"])
    return f"{line}  ({'; '.join(facts)})" if facts else line
