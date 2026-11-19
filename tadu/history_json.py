"""JSON-ready form of one history entry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.item_changes import item_changes
from tadu.line_changes import line_changes

if TYPE_CHECKING:
    from tadu.history_entry import HistoryEntry
    from tadu.history_event import HistoryEvent


def history_json(event: HistoryEvent) -> HistoryEntry:
    """The commit (null fields for uncommitted changes), the changes, and both texts of the item."""
    commit, before, after = event.commit, event.before, event.after
    return {
        "commit": commit.sha if commit else None,
        "short": commit.short if commit else None,
        "parents": list(commit.parents) if commit else [],
        "date": commit.date if commit else None,
        "author": commit.author if commit else None,
        "subject": commit.subject if commit else None,
        "merge": bool(commit and len(commit.parents) > 1),
        "created": before is None,
        "path": after.path,
        "changes": [
            {"field": fact, "before": old, "after": new}
            for fact, old, new in item_changes(before, after)
        ],
        "lines": [
            {"op": op, "field": field, "text": text}
            for op, field, text in line_changes(before, after)
        ],
        "before_text": before.text if before else None,
        "after_text": after.text,
    }
