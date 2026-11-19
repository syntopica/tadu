"""The kind of one change of a backlog item."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.state_names import STATE_NAMES

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

CLOSING = {"done": "closed", "cancelled": "cancelled"}
OPENING = {"in_progress": "started", "blocked": "blocked"}


def change_event(before: BacklogItem | None, after: BacklogItem | None, *, migrated: bool) -> str:
    """One of CHANGE_EVENTS, from the item's state before and after the change.

    No item before is `created` (`migrated` when `tadu migrate` made it), none after is
    `removed`. A state that became done or cancelled is `closed` or `cancelled`; one that left
    them is `reopened`; one that became in progress or blocked is `started` or `blocked`.
    Anything else, such as a field edit or going back to pending, is `changed`.
    """
    if after is None or before is None:
        return "removed" if after is None else ("migrated" if migrated else "created")
    old, new = STATE_NAMES.get(before.state), STATE_NAMES.get(after.state)
    if old == new or new is None:
        return "changed"
    if new in CLOSING:
        return CLOSING[new]
    return "reopened" if old in CLOSING else OPENING.get(new, "changed")
