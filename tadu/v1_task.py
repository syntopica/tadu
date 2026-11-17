"""Convert one tadu v1 item into a task (format v2)."""

from __future__ import annotations

import re

from tadu.item_state_pattern import ITEM_STATE_PATTERN
from tadu.legacy_closing_fields import legacy_closing_fields
from tadu.read_v1_continuation import read_v1_continuation
from tadu.split_blocker import split_blocker
from tadu.split_bold_title import split_bold_title
from tadu.split_long_title import split_long_title
from tadu.stable_task_id import stable_task_id
from tadu.task_defaults import DEFAULT_TASK_TYPES, UNKNOWN_CATEGORY, UNKNOWN_PRIORITY, UNKNOWN_TYPE
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.unique_in_order import unique_in_order

STATES = {" ": "pending", "~": "in_progress", "!": "blocked", "x": "done", "-": "cancelled"}
CATEGORY = re.compile(r"^\*\*([^*\n]+):\*\* ")


def v1_task(
    block: tuple[str, ...], section: str | None, source: str
) -> tuple[dict[str, object], str]:
    """The task and the display name of its category (the **Category:** prefix, else the section).

    Unknown values get the defaults: category general, type untriaged, priority untriaged. An
    item without an ID gets a stable one derived from `source` (file and position) and its title.
    """
    match = ITEM_STATE_PATTERN.match(block[0])
    marker, day, text = match.groups() if match else (" ", None, block[0])
    prefix = CATEGORY.match(text)
    shown = prefix.group(1) if prefix else section or "General"
    bold_title, bold_rest = split_bold_title((text[prefix.end() :] if prefix else text).strip())
    title, lead = split_long_title(bold_title)
    lead = " ".join(part for part in (lead, bold_rest) if part)
    parts = read_v1_continuation(block[1:])
    notes = [lead, *([""] if parts.notes else []), *parts.notes] if lead else parts.notes
    fields, bullets, state = parts.fields, parts.bullets, STATES[marker]
    labels = [label.strip() for label in fields.get("Labels", "").split(",") if label.strip()]
    kind = next((label for label in labels if label in DEFAULT_TASK_TYPES), UNKNOWN_TYPE)
    blocker = unblock = ""
    if state == "blocked" and notes:
        blocker, unblock, notes = split_blocker(notes)
    estimate = fields.get("Estimate", "")
    closing = legacy_closing_fields(
        state,
        day,
        {
            "title": title.rstrip("."),
            "result": " ".join(bullets.get("Result", [])),
            "evidence": [line for line in bullets.get("Evidence", []) if line],
            "resolution": " ".join(bullets.get("Resolution", [])),
        },
    )
    task: dict[str, object] = {
        "tadu": TASK_FORMAT_VERSION,
        "id": fields.get("ID") or stable_task_id(source, title),
        "title": title.rstrip("."),
        "state": state,
        "category": re.sub(r"[^a-z0-9]+", "-", shown.lower()).strip("-") or UNKNOWN_CATEGORY,
        "type": kind,
        "priority": fields.get("Priority", UNKNOWN_PRIORITY),
        "labels": [label for label in labels if label != kind],
        "due": fields.get("Due"),
        "queue": "ready" if fields.get("Queue") == "ready" and state == "pending" else None,
        "assignees": [a.strip() for a in fields.get("Assignees", "").split(",") if a.strip()],
        "estimate": int(estimate) if estimate.isdigit() else None,
        "blocked_by": parts.blocked_by,
        "blocker": blocker,
        "unblock": unblock,
        "notes": notes,
        "done_when": parts.done_when,
        "created": None if closing["closed"] else day,
        **closing,
        "files": unique_in_order(
            f.strip(" `.") for f in ", ".join(bullets.get("Files", [])).split(",")
        ),
    }
    return task, shown
