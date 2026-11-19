"""What a task converted from format 1 holds that the task already in todo/ does not."""

from __future__ import annotations

from tadu.task_field_kinds import TASK_LINE_KEYS
from tadu.task_key_order import TASK_KEY_ORDER

SAME_TASK = ("tadu", "id")


def lacking_lines(converted: dict[str, object], existing: dict[str, object]) -> list[str]:
    """One note line for each value of `converted` that `existing` lacks, in key order.

    A Markdown line of the notes that `existing` lacks is kept as it is; any other value is
    written `key: value`, a list with only the elements `existing` lacks.
    """
    lines: list[str] = []
    for key in TASK_KEY_ORDER:
        value, held = converted.get(key), existing.get(key)
        if key in SAME_TASK or value in (None, "", [], {}) or value == held:
            continue
        if isinstance(value, list):
            had = held if isinstance(held, list) else []
            missing = [item for item in value if item not in had and item != ""]
            if key == "notes":
                lines += [str(item) for item in missing]
            elif key in TASK_LINE_KEYS:
                lines += [f"{key}: {item}" for item in missing]
            elif missing:
                lines.append(f"{key}: {', '.join(str(item) for item in missing)}")
        else:
            lines.append(f"{key}: {value}")
    return lines
