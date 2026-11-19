"""The hook operation."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param

HOOK_OPERATION = Operation(
    "hook",
    "agent hooks that run doctor after a backlog change",
    (
        Param(
            "agent",
            "choice",
            "claude: a Claude Code PostToolUse hook",
            ("claude",),
            required=True,
            positional=True,
        ),
    ),
    access="local",
    target="none",
)
