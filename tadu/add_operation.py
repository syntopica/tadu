"""The add operation, for both backlog formats."""

from __future__ import annotations

from tadu.add_field_params import ADD_FIELD_PARAMS
from tadu.kinds import KINDS
from tadu.operation import Operation
from tadu.param import Param
from tadu.task_link_params import TASK_LINK_PARAMS
from tadu.task_priorities import TASK_PRIORITIES

ADD_OPERATION = Operation(
    "add",
    "add a task (format 2, after showing similar ones) or one TODO.md item, such as "
    "a decision for a person (`--kind decision`) met while working alone",
    (
        Param("title", "text", "one line, imperative", required=True),
        Param(
            "category",
            "text",
            "format 1: the ## section, as **Category:**; format 2: category slug "
            "(default: general)",
        ),
        Param("type", "text", "type slug (default: untriaged)", format=2),
        Param(
            "priority",
            "choice",
            "item priority; untriaged is for tasks (format 2: default untriaged)",
            TASK_PRIORITIES,
        ),
        Param(
            "kind",
            "choice",
            "task, decision, waiting or later (default: none)",
            KINDS,
            format=1,
        ),
        Param("milestone", "text", "milestone slug declared in todo/tadu.json", format=2),
        *ADD_FIELD_PARAMS,
        Param("no_id", "flag", "do not give the item an ID", format=1),
        *TASK_LINK_PARAMS,
    ),
    access="write",
    describe="Add one open item: a TODO.md item, or a task file in a format 2 backlog (after "
    "showing similar ones). When you meet a question only a person can answer, add it with kind "
    "`decision`, the options and their trade-offs as notes, then go on with other work instead "
    "of waiting or guessing.",
)
