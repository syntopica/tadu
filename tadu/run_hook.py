"""The hook command: tadu doctor after a Claude Code tool call changed a backlog."""

from __future__ import annotations

import json

from tadu.hook_backlog_root import hook_backlog_root
from tadu.hook_report import hook_report


def run_hook(stdin_text: str) -> str | None:
    """The PostToolUse JSON to print, or None to stay silent; malformed input is ignored."""
    try:
        payload: object = json.loads(stdin_text)
    except ValueError:
        return None
    root = hook_backlog_root(payload)
    report = None if root is None else hook_report(root, 20)
    if report is None:
        return None
    output = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": report}}
    return json.dumps(output)
