"""Everything wrong with a task backlog's configuration."""

from __future__ import annotations

from tadu.archive_policy_problems import archive_policy_problems
from tadu.label_pattern import LABEL_PATTERN
from tadu.list_check import list_check
from tadu.milestone_problems import milestone_problems
from tadu.task_format_version import TASK_FORMAT_VERSION

CONFIG_KEYS = ("tadu", "categories", "types", "milestones", "stale_after_days", "archive")
CHECK_TYPES = list_check(lambda item: bool(LABEL_PATTERN.match(item)), "slugs")


def todo_config_problems(config: dict[str, object]) -> tuple[str, ...]:
    """Messages for todo/tadu.json; empty when it is valid. x- keys are left to teams."""
    problems = [
        f"unknown key {key}"
        for key in config
        if key not in CONFIG_KEYS and not key.startswith("x-")
    ]
    if config.get("tadu") != TASK_FORMAT_VERSION or isinstance(config.get("tadu"), bool):
        problems.append(f"tadu must be {TASK_FORMAT_VERSION}")
    categories = config.get("categories")
    if not isinstance(categories, dict) or not categories:
        problems.append("categories must be a non-empty object of slug -> name")
    elif any(
        not LABEL_PATTERN.match(k) or not isinstance(v, str) or not v for k, v in categories.items()
    ):
        problems.append("categories must map slugs to names")
    if "types" in config and (message := CHECK_TYPES(config["types"])):
        problems.append(f"types {message}")
    if "milestones" in config:
        problems += milestone_problems(config["milestones"])
    stale = config.get("stale_after_days", 1)
    if isinstance(stale, bool) or not isinstance(stale, int) or stale < 1:
        problems.append("stale_after_days must be a whole number from 1")
    if "archive" in config:
        problems += archive_policy_problems(config["archive"])
    return tuple(problems)
