"""Validate the milestones of a task backlog's configuration."""

from __future__ import annotations

from tadu.check_task_slug import check_task_slug
from tadu.check_task_text import check_task_text
from tadu.is_real_date import is_real_date


def milestone_problems(value: object) -> tuple[str, ...]:
    """Messages for a milestones value that is not slug -> {"name": text, "due": date}."""
    if not isinstance(value, dict):
        return ("milestones must be an object of slug -> {name, due}",)
    problems: list[str] = []
    for slug, entry in value.items():
        if check_task_slug(slug) or not isinstance(entry, dict):
            problems.append(f"milestone {slug!r} must be a slug with a {{name, due}} object")
        elif check_task_text(entry.get("name")) or set(entry) - {"name", "due"}:
            problems.append(f"milestone {slug!r} needs a name and allows only name and due")
        elif "due" in entry and not is_real_date(entry["due"]):
            problems.append(f"milestone {slug!r} due must be a YYYY-MM-DD date")
    return tuple(problems)
