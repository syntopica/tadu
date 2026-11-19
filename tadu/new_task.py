"""Build the task `tadu add` writes."""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING

from tadu.resolve_task_ids import resolve_task_ids
from tadu.split_list_value import split_list_value
from tadu.task_defaults import UNKNOWN_CATEGORY, UNKNOWN_PRIORITY, UNKNOWN_TYPE
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.unique_in_order import unique_in_order

if TYPE_CHECKING:
    import argparse
    from datetime import date
    from pathlib import Path


def new_task(args: argparse.Namespace, today: date, todo: Path) -> dict[str, object]:
    """A pending task (blocked when it is blocked by other tasks) with a fresh UUID4 id.

    Relation ids may be given as unique prefixes; they are stored in full. created_by is
    --created-by, else $TADU_ACTOR. The format 1 spellings are the same keys: --not-before is
    defer_until, and the comma lists of --labels and --assignees join --label and --assignee.
    """
    blocked_by = resolve_task_ids(todo, args.blocked_by)
    # keys: the two fixed relation names
    single = {
        key: resolve_task_ids(todo, [value])[0] if value else None
        for key, value in (("parent", args.parent), ("discovered_from", args.discovered_from))
    }
    return {
        "tadu": TASK_FORMAT_VERSION,
        "id": f"t-{uuid.uuid4()}",
        "title": args.title,
        "state": "blocked" if blocked_by else "pending",
        "category": args.category or UNKNOWN_CATEGORY,
        "type": args.type or UNKNOWN_TYPE,
        "priority": args.priority or UNKNOWN_PRIORITY,
        "kind": args.kind,
        "labels": unique_in_order([*(args.label or ()), *split_list_value(args.labels or "")]),
        "milestone": args.milestone,
        "created": today.isoformat(),
        "created_by": args.created_by or os.environ.get("TADU_ACTOR"),
        "due": args.due,
        "defer_until": args.defer_until or args.not_before,
        "check_on": args.check_on,
        "queue": args.queue,
        "assignees": unique_in_order(
            [*(args.assignee or ()), *split_list_value(args.assignees or "")]
        ),
        "estimate": args.estimate,
        **single,
        "blocked_by": blocked_by,
        "related": resolve_task_ids(todo, args.related),
        "notes": args.note,
        "done_when": args.done_when,
        "links": args.link,
    }
