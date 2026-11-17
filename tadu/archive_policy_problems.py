"""Validate the archive policy of a task backlog's configuration."""

from __future__ import annotations

POLICY_KEYS = ("after_days", "keep_closed", "month_folders_min")


def archive_policy_problems(value: object) -> tuple[str, ...]:
    """Messages unless the value is an object of positive whole numbers with a rule to archive by."""
    if not isinstance(value, dict):
        return ("archive must be an object",)
    problems = [f"archive has an unknown key {key}" for key in value if key not in POLICY_KEYS]
    for key in POLICY_KEYS:
        number = value.get(key)
        if key in value and (isinstance(number, bool) or not isinstance(number, int) or number < 1):
            problems.append(f"archive {key} must be a whole number from 1")
    if "after_days" not in value and "keep_closed" not in value:
        problems.append("archive needs after_days, keep_closed, or both")
    return tuple(problems)
