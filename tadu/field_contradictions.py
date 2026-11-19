"""Field values of one open item that contradict each other or its state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.field_names import MARKDOWN_NAMES

if TYPE_CHECKING:
    from datetime import date

    from tadu.backlog_item import BacklogItem
    from tadu.field_names import FieldNames


def field_contradictions(
    item: BacklogItem, today: date, names: FieldNames = MARKDOWN_NAMES
) -> list[tuple[str, str]]:
    """(field name the finding points at, message) for each contradiction, in a fixed order.

    Only contradictions that hold whatever the item means are reported: a blocked
    `[!]` item may be of any kind, so the state alone never contradicts a kind. The first
    element is always the format 1 field name; `names` words the message for its format.
    """
    fields, found, n = item.fields, [], names
    due, start, check = fields.due, fields.not_before, fields.check_on
    if due is not None and start is not None and start > due:
        found.append(("Not before", f"{n.not_before} {start} is after {n.due} {due}"))
    if due is not None and check is not None and check > due:
        found.append(("Check on", f"{n.check_on} {check} is after {n.due} {due}"))
    if item.state == "~" and start is not None and start > today:
        found.append(
            ("Not before", f"the {n.thing} is in progress but {n.not_before} {start} is ahead")
        )
    if item.state == "~" and fields.kind == "later":
        found.append(("Kind", f"{n.kind}{n.value}later contradicts {n.a_thing} in progress"))
    if fields.queue == "ready" and fields.kind in ("waiting", "later"):
        found.append(
            ("Queue", f"{n.queue}{n.value}ready contradicts {n.kind}{n.value}{fields.kind}")
        )
    return found
