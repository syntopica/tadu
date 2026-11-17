"""The one accepted text of a task file."""

from __future__ import annotations

import json

from tadu.task_field_kinds import TASK_LINE_KEYS
from tadu.task_key_order import TASK_KEY_ORDER
from tadu.trim_blank_lines import trim_blank_lines


def canonical_task_text(task: dict[str, object]) -> str:
    """Known keys in canonical order, unknown keys after them, x- keys last; no empty values.

    Two-space indent, one array element per line, UTF-8 and a final newline: the same task
    always gives the same bytes, so a diff shows only real changes.
    """
    cleaned: dict[str, object] = {}
    for key, raw in task.items():
        value = trim_blank_lines(raw) if key in TASK_LINE_KEYS and isinstance(raw, list) else raw
        if value not in (None, "", [], {}):
            cleaned[key] = value
    known = [key for key in TASK_KEY_ORDER if key in cleaned]
    unknown = [key for key in cleaned if key not in TASK_KEY_ORDER and not key.startswith("x-")]
    extensions = sorted(key for key in cleaned if key.startswith("x-"))
    ordered = {key: cleaned[key] for key in (*known, *unknown, *extensions)}
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
