"""Decide which backlog, if any, a Claude Code tool call changed."""

from __future__ import annotations

from pathlib import Path

from tadu.backlog_file_names import BACKLOG_FILE_NAMES
from tadu.backlog_write_pattern import (
    BACKLOG_NAME_PATTERN,
    LEADING_CD_PATTERN,
    SHELL_WRITE_PATTERN,
    TADU_CLOSE_WRITE_PATTERN,
)
from tadu.nearest_backlog_root import nearest_backlog_root
from tadu.payload_text import payload_text


def hook_backlog_root(payload: object) -> Path | None:
    """The root of the backlog an edit or a shell write touched; the command is read, never run."""
    tool = payload_text(payload, "tool_name")
    cwd = Path(payload_text(payload, "cwd") or ".")
    if tool in ("Edit", "Write", "MultiEdit"):
        path = Path(payload_text(payload, "tool_input", "file_path"))
        return nearest_backlog_root(path.parent) if path.name in BACKLOG_FILE_NAMES else None
    command = payload_text(payload, "tool_input", "command")
    edits = BACKLOG_NAME_PATTERN.search(command) and SHELL_WRITE_PATTERN.search(command)
    if tool != "Bash" or not (edits or TADU_CLOSE_WRITE_PATTERN.search(command)):
        return None
    lead = LEADING_CD_PATTERN.match(command)
    start = cwd / Path(lead.group(1).strip("\"'")).expanduser() if lead else cwd
    return nearest_backlog_root(start)
