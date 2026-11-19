"""The parts of a Markdown backlog item that history reports one by one."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.iso_date import iso_date
from tadu.state_names import STATE_NAMES

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem


def item_facts(item: BacklogItem | None) -> dict[str, str | None]:
    """Each fact as text, None when absent; always the same keys in the same order.

    The keys are those of `tadu list --json`, with `file` for the path. A queue of `backlog`
    is the default and counts as absent. No item (before it was created) has every fact absent.
    """
    fields = item.fields if item else None
    facts: dict[str, str | None] = {
        "file": item.path if item else None,
        "state": STATE_NAMES.get(item.state, item.state) if item else None,
        "day": iso_date(item.day) if item else None,
        "title": item.title if item else None,
        "id": fields.id if fields else None,
        "priority": fields.priority if fields else None,
        "assignees": ", ".join(fields.assignees) if fields else None,
        "due": iso_date(fields.due) if fields else None,
        "check_on": iso_date(fields.check_on) if fields else None,
        "not_before": iso_date(fields.not_before) if fields else None,
        "labels": ", ".join(fields.labels) if fields else None,
        "queue": fields.queue if fields and fields.queue != "backlog" else None,
        "kind": fields.kind if fields else None,
        "estimate": str(fields.estimate) if fields and fields.estimate is not None else None,
    }
    # keys: the literal keys above, each once; only empty values become None
    return {key: value or None for key, value in facts.items()}
