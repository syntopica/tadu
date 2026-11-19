"""The fields `add` gives a new item: dates, people, labels, queue and estimate."""

from __future__ import annotations

from tadu.param import Param
from tadu.queues import QUEUES

ADD_FIELD_PARAMS = (
    Param("due", "text", "deadline, YYYY-MM-DD", metavar="YYYY-MM-DD"),
    Param(
        "defer_until",
        "text",
        "not before this day, YYYY-MM-DD",
        metavar="YYYY-MM-DD",
        format=2,
    ),
    Param(
        "check_on",
        "text",
        "YYYY-MM-DD, when to look at it again",
        metavar="YYYY-MM-DD",
        format=1,
    ),
    Param(
        "not_before",
        "text",
        "YYYY-MM-DD, it cannot start before this day",
        metavar="YYYY-MM-DD",
        format=1,
    ),
    Param(
        "assignees",
        "list",
        "person id or agent:<name>; repeat or comma-separate",
        flags=("--assignee", "--assignees"),
        metavar="PERSON",
    ),
    Param(
        "labels",
        "list",
        "label; repeat or comma-separate",
        flags=("--label", "--labels"),
        metavar="LABEL",
    ),
    Param("queue", "choice", "ready = can start now", QUEUES),
    Param("estimate", "count", "minutes", metavar="MINUTES"),
)
