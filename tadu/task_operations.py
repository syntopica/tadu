"""The operations that change an item named by its key: set and claim."""

from __future__ import annotations

from dataclasses import replace

from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import ITEM_ID

KEY = replace(ITEM_ID, positional=True, exclusive="")

TASK_OPERATIONS = (
    Operation(
        "set",
        "change fields of a task (format 2)",
        (
            replace(KEY, help="the task's id, or a unique prefix of it (10 characters or more)"),
            Param(
                "changes",
                "words",
                "key=value, key+=value or key-=value for lists, key= to remove",
                required=True,
                positional=True,
                aliases=("change",),
            ),
        ),
        access="write",
        target="root",
    ),
    Operation(
        "claim",
        "take an item: assignee, in progress and (format 2) started",
        (
            KEY,
            Param(
                "who",
                "text",
                "person id or agent:<name>",
                required=True,
                flags=("--as",),
                aliases=("person",),
            ),
            Param("force", "flag", "take over an item someone else has in progress"),
        ),
        access="write",
        target="root",
    ),
)
