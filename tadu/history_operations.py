"""The operations that read one item, or what changed in git."""

from __future__ import annotations

from dataclasses import replace

from tadu.change_event_list import change_event_list
from tadu.change_events import CHANGE_EVENTS
from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import AUTHOR, DONE_DAYS, FIELD

NARROW = "history filters (each implies --history)"

HISTORY_OPERATIONS = (
    Operation(
        "show",
        "print one backlog item by key",
        (
            Param("key", "text", "item key", required=True, positional=True, aliases=("id",)),
            DONE_DAYS,
            Param("json", "flag", "print the item as JSON"),
            Param(
                "history",
                "flag",
                "also print each change git recorded to the item, newest first (any age)",
            ),
            replace(FIELD, section=NARROW),
            Param("since", "day", "commits from this day on", section=NARROW),
            Param("until", "day", "commits up to this day", section=NARROW),
            replace(AUTHOR, section=NARROW),
        ),
        describe="The full text of one item by its key (its ID:, or the k- key `list` gives with "
        "json). With `history`, each change git recorded to it follows, newest first; `field`, "
        "`since`, `until` and `author` narrow that history (any of them implies `history`), "
        'such as field ["state", "assignee"] for who took it and when it moved.',
    ),
    Operation(
        "changes",
        "what changed across the backlog in a range of days, for a retro",
        (
            Param("since", "day", "first day (default: 14 days ago)"),
            Param("until", "day", "last day (default: today)"),
            Param(
                "event",
                "list",
                f"only these changes: {', '.join(CHANGE_EVENTS)}; repeat or comma-separate",
                default=[],
                metavar="KIND",
                parse=change_event_list,
                aliases=("events",),
            ),
            AUTHOR,
            FIELD,
            Param("json", "flag", "one JSON object per change"),
        ),
        describe="What changed across the backlog in a range of days, for a retro or a status "
        "report: what was closed and by whom, what was reopened, started, blocked, created or "
        "edited, grouped by kind, newest first. The last 14 days unless `since` and `until` say.",
    ),
)
