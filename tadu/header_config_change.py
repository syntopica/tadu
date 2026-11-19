"""Keep the format 1 headers in todo/tadu.json."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.read_text_exact import read_text_exact
from tadu.read_todo_config import read_todo_config
from tadu.todo_layout import TODO_CONFIG

if TYPE_CHECKING:
    from pathlib import Path

HEADER_KEY = "x-format-1-header"


def header_config_change(todo: Path, header: dict[str, list[str]]) -> tuple[Path, str, str] | None:
    """(path, text read, new text) adding each header line tadu.json lacks; None when it has all.

    A header already kept stays as it is; a line it lacks is appended, so nothing is lost.
    TaskFileError when tadu.json is not a JSON object.
    """
    path = todo / TODO_CONFIG
    before = read_text_exact(path)
    config = read_todo_config(todo)
    held = config.get(HEADER_KEY)
    kept = dict(held) if isinstance(held, dict) else {}
    changed = False
    for name, lines in header.items():
        held = kept.get(name)
        have: list[object] = held if isinstance(held, list) else []
        missing = [line for line in lines if line and line not in have]
        if name not in kept or missing:
            # keys: the two file names
            kept[name] = [*have, *missing] if have else lines
            changed = True
    if not changed:
        return None
    after = json.dumps({**config, HEADER_KEY: kept}, indent=2, ensure_ascii=False) + "\n"
    return path, before, after
