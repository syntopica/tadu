"""The hook operation."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param

HOOK_OPERATION = Operation(
    "hook",
    "agent hooks for backlog context and validation",
    (
        Param(
            "agent",
            "choice",
            "claude: PostToolUse validation; codex: prompt briefing and PostToolUse validation",
            ("claude", "codex"),
            required=True,
            positional=True,
        ),
    ),
    access="local",
    target="none",
)
