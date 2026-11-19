"""What the fields doctor compares are called in each backlog format."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldNames:
    """The names doctor's messages use for one format.

    The date and choice fields, how a value follows its name, and the thing (with its
    article) the fields belong to.
    """

    due: str
    not_before: str
    check_on: str
    kind: str
    queue: str
    value: str
    thing: str
    a_thing: str


MARKDOWN_NAMES = FieldNames(
    "Due", "Not before", "Check on", "Kind", "Queue", ": ", "item", "an item"
)
TASK_NAMES = FieldNames("due", "defer_until", "check_on", "kind", "queue", " ", "task", "a task")
