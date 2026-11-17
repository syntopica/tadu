"""Field values of one open item that contradict each other or its state."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from tadu.backlog_item import BacklogItem


def field_contradictions(item: BacklogItem, today: date) -> list[tuple[str, str]]:
    """(field name the finding points at, message) for each contradiction, in a fixed order.

    Only contradictions that hold whatever the item means are reported: a blocked
    `[!]` item may be of any kind, so the state alone never contradicts a kind.
    """
    fields, found = item.fields, []
    due, start, check = fields.due, fields.not_before, fields.check_on
    if due is not None and start is not None and start > due:
        found.append(("Not before", f"Not before {start} is after Due {due}"))
    if due is not None and check is not None and check > due:
        found.append(("Check on", f"Check on {check} is after Due {due}"))
    if item.state == "~" and start is not None and start > today:
        found.append(("Not before", f"the item is in progress but Not before {start} is ahead"))
    if item.state == "~" and fields.kind == "later":
        found.append(("Kind", "Kind: later contradicts an item in progress"))
    if fields.queue == "ready" and fields.kind in ("waiting", "later"):
        found.append(("Queue", f"Queue: ready contradicts Kind: {fields.kind}"))
    return found
