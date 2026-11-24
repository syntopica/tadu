"""The native Codex prompt and post-tool hook adapter."""

from __future__ import annotations

import json

from tadu.codex_hook_output import codex_hook_output
from tadu.workspace_error import WorkspaceError


def run_codex_hook(stdin_text: str) -> str | None:
    """Return native additionalContext without allowing a hook failure to block the turn."""
    try:
        payload: object = json.loads(stdin_text)
        if not isinstance(payload, dict):
            return None
        return codex_hook_output(payload)
    except (ValueError, OSError, WorkspaceError):
        return None
