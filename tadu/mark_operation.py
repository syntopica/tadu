"""The mark operation, for both backlog formats."""

from __future__ import annotations

from tadu.kinds import KINDS
from tadu.mark_states import MARK_STATES
from tadu.operation import Operation
from tadu.param import Param
from tadu.priorities import PRIORITIES
from tadu.queues import QUEUES
from tadu.shared_params import ITEM_ID, ITEM_MATCH

MARK_OPERATION = Operation(
    "mark",
    "set one open item's state or fields: blocked with the blocker named (such as a "
    "decision added for a person), open again once unblocked, or in_progress",
    (
        ITEM_ID,
        ITEM_MATCH,
        Param("state", "choice", "new state", tuple(MARK_STATES)),
        Param("kind", "choice", "set the item's Kind:", KINDS, format=1),
        Param("priority", "choice", "set the priority", PRIORITIES),
        Param(
            "assignees",
            "list",
            "set the assignees: person ids; repeat or comma-separate",
            flags=("--assignee", "--assignees"),
            metavar="PERSON",
        ),
        Param("due", "text", "set the deadline, YYYY-MM-DD", metavar="YYYY-MM-DD"),
        Param("check_on", "text", "set Check on:, YYYY-MM-DD", metavar="YYYY-MM-DD", format=1),
        Param(
            "not_before",
            "text",
            "set Not before: (format 2: defer_until), YYYY-MM-DD",
            metavar="YYYY-MM-DD",
        ),
        Param(
            "labels",
            "list",
            "set the labels; repeat or comma-separate",
            flags=("--label", "--labels"),
            metavar="LABEL",
        ),
        Param("queue", "choice", "set the queue: backlog or ready", QUEUES),
        Param("estimate", "count", "set the estimate, in minutes", metavar="MINUTES"),
        Param("note", "text", "a paragraph added to the item; required for blocked"),
    ),
    access="write",
    describe="Set one open item's state: `blocked` with a note naming the blocker (such as "
    "the decision you added), `open` once it is unblocked, or `in_progress`. Also sets or "
    "changes its fields, such as priority or assignees, without editing the files.",
)
