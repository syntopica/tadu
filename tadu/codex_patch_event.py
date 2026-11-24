"""Adapt Codex patch file headers to the backlog-write detector."""

from __future__ import annotations

import re
from pathlib import Path

from tadu.backlog_file_names import BACKLOG_FILE_NAMES


def codex_patch_event(payload: dict[str, object]) -> dict[str, object]:
    """Locate a backlog file in a patch without interpreting or executing its contents."""
    inputs = payload.get("tool_input")
    patch = inputs.get("command", inputs.get("input")) if isinstance(inputs, dict) else inputs
    if not isinstance(patch, str):
        return payload
    cwd = Path(str(payload.get("cwd") or "."))
    for header in re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", patch, re.MULTILINE):
        path = cwd / header
        # path-name: compare patch file names with the backlog file names, retaining the full path.
        if path.name in BACKLOG_FILE_NAMES or (path.suffix == ".json" and "todo" in path.parts):
            return {**payload, "tool_name": "Write", "tool_input": {"file_path": str(path)}}
    return payload
