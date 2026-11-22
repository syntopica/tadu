"""The operations that read the backlog by who has to act."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import JSON_ITEMS, PAGE, PERSON

ATTENTION_OPERATIONS = (
    Operation(
        "ready",
        "print the open items nothing blocks or defers, most urgent first",
        (
            JSON_ITEMS,
            Param(
                "with_deferred_children",
                "flag",
                "also list the children of a deferred parent",
            ),
            *PAGE,
        ),
    ),
    Operation(
        "next",
        "tasks an agent can do now without a person, most pressing first "
        "(for 'work alone', 'I will be away')",
        (JSON_ITEMS, PERSON),
        describe="Tasks you can do now without a person, most pressing first. Use it when the "
        "user asks you to work alone or will be away (AFK). It leaves out decisions, waiting and "
        "later items, blocked tasks, items whose Not before day is ahead and tasks assigned "
        "only to someone else. Items without a kind are included as work.",
    ),
    Operation(
        "inbox",
        "what waits on a person: decisions, due follow-ups and checks, their blocked "
        "tasks (for 'what is waiting for me', 'I am here')",
        (JSON_ITEMS, PERSON),
        describe="What waits on a person: decisions to make, follow-ups and checks whose date "
        "has come, and their blocked tasks. Use it when the user is present or asks what is "
        "waiting for them.",
    ),
    Operation(
        "urgent",
        "urgent or high priority items and items due soon, by who acts (for 'what is urgent')",
        (
            JSON_ITEMS,
            Param(
                "days",
                "count",
                "a date within this many days counts as due soon (default: 1, by tomorrow)",
                default=1,
            ),
        ),
        describe="Urgent or high priority items and items due soon or overdue, grouped by who "
        "acts (do, decide, chase, check, blocked). Use it when the user asks what is urgent.",
    ),
    Operation(
        "prime",
        "a short briefing for an agent: open counts, the next tasks and the workflow's commands",
        (PERSON,),
        describe="A short briefing to read before working the backlog: how many items are open, "
        "the first tasks next gives, how many wait on a person or are urgent, and the commands "
        "of the workflow for this backlog's format. Call it when you start a session.",
    ),
)
