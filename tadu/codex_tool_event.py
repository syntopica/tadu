"""Adapt Codex shell calls to the existing backlog-write detector."""

from __future__ import annotations

from tadu.codex_patch_event import codex_patch_event


def codex_tool_event(payload: dict[str, object]) -> dict[str, object]:
    """Normalize exec_command's cmd/workdir, preserving already-compatible tool events."""
    inputs = payload.get("tool_input")
    if payload.get("tool_name") in ("apply_patch", "functions.apply_patch"):
        return codex_patch_event(payload)
    if payload.get("tool_name") in ("exec_command", "functions.exec_command") and isinstance(
        inputs, dict
    ):
        return {
            **payload,
            "tool_name": "Bash",
            "cwd": inputs.get("workdir") or payload.get("cwd"),
            "tool_input": {"command": inputs.get("cmd")},
        }
    return payload
