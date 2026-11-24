"""Render a validated native Codex hook event."""

from __future__ import annotations

import json

from tadu.codex_prompt_context import codex_prompt_context
from tadu.codex_tool_event import codex_tool_event
from tadu.run_hook import run_hook


def codex_hook_output(payload: dict[str, object]) -> str | None:
    """Dispatch supported events and serialize prompt context in the native hook shape."""
    event = payload.get("hook_event_name", "UserPromptSubmit")
    if event == "PostToolUse":
        return run_hook(json.dumps(codex_tool_event(payload)))
    context = codex_prompt_context(payload) if event == "UserPromptSubmit" else None
    if context is None:
        return None
    return json.dumps(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    )
