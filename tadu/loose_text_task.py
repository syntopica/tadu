"""Turn a block of format 1 text written outside every item into a task holding it."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from tadu.legacy_closing_fields import LEGACY_NOTE
from tadu.split_long_title import split_long_title
from tadu.stable_task_id import stable_task_id
from tadu.task_defaults import UNKNOWN_CATEGORY, UNKNOWN_PRIORITY, UNKNOWN_TYPE
from tadu.task_format_version import TASK_FORMAT_VERSION

HEADING = re.compile(r"#+\s+(?:\d{4}(?:-\d{2}(?:-\d{2})?)?(?![\d-]))?[\s—:-]*(.*)")
PRECISION = {4: "year", 7: "month"}
DAY_LENGTH = 10
OPEN_NOTE = (
    "Kept from TODO.md line {line}, written outside its items: no task held it when the "
    "backlog was migrated. Move it into the task it belongs to, or make it one."
)


def loose_text_task(name: str, first: int, lines: list[str], day: str | None) -> dict[str, object]:
    """A task holding the block whole in its notes, after a line saying what was assumed.

    Only what is sure becomes a key: the title is the block's heading (without its date),
    else its first line. A block of TODO_LOG.md, such as an old prose entry, is closed as
    done on the day the log gives (a month or a year gives its first day, no date the
    migration day) with the legacy evidence line, as the log records no state, result or
    evidence for it. A block of TODO.md is pending and untriaged, to be sorted.
    """
    heading = HEADING.fullmatch(lines[0])
    text = (heading.group(1) if heading else "") or next(
        (line.strip(" #-*") for line in lines if line.strip(" #-*")), "Loose text"
    )
    title = split_long_title(text.strip())[0].rstrip(".") or "Loose text"
    task: dict[str, object] = {
        "tadu": TASK_FORMAT_VERSION,
        "id": stable_task_id(f"{name}:loose:{first + 1}", title),
        "title": title,
        "state": "pending",
        "category": UNKNOWN_CATEGORY,
        "type": UNKNOWN_TYPE,
        "priority": UNKNOWN_PRIORITY,
        "notes": [OPEN_NOTE.format(line=first + 1), "", *lines],
    }
    if name == "TODO.md":
        return task
    today = datetime.now(UTC).date().isoformat()
    closed = {DAY_LENGTH: day, 7: f"{day}-01", 4: f"{day}-01-01"}.get(len(day or ""), today)
    if day is None:
        dated = " It has no date, so it is closed on the day it was migrated."
    elif len(day) == DAY_LENGTH:
        dated = ""
    else:
        precision = PRECISION[len(day)]
        dated = (
            f" It has no day: the log put it in the {precision} {day}, so it is closed on {closed}."
        )
    note = (
        f"Migrated from TODO_LOG.md line {first + 1}, written outside its dated entries; the "
        f"log records no state, result or evidence for it, so it is closed as done.{dated}"
    )
    return {
        **task,
        "state": "done",
        "notes": [note, "", *lines],
        "closed": closed,
        "result": title,
        "evidence": [f"{LEGACY_NOTE} evidence"],
    }
