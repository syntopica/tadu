"""The text of a new todo/tadu.json."""

from __future__ import annotations

import json

from tadu.task_format_version import TASK_FORMAT_VERSION


def fresh_todo_config_text(categories: dict[str, str] | None = None) -> str:
    """Format version and categories (general when none are given), as canonical JSON."""
    config = {
        "tadu": TASK_FORMAT_VERSION,
        "categories": dict(sorted((categories or {"general": "General"}).items())),
    }
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"
