"""Everything wrong with one task object."""

from __future__ import annotations

from tadu.task_field_kinds import TASK_REQUIRED_KEYS
from tadu.task_rule_problems import task_rule_problems
from tadu.task_value_checks import TASK_VALUE_CHECKS


def task_problems(task: dict[str, object]) -> tuple[str, ...]:
    """Missing required keys, invalid values, then state rules; empty when the task is valid.

    Keys this tool does not know are not problems here: they are kept on rewrite, and doctor
    reports them separately in case of a typo.
    """
    problems = [f"missing {key}" for key in TASK_REQUIRED_KEYS if key not in task]
    for key, value in task.items():
        check = TASK_VALUE_CHECKS.get(key)
        message = check(value) if check else None
        if message:
            problems.append(f"{key} {message}")
    return (*problems, *task_rule_problems(task))
