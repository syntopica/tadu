"""The operations that only run on this machine: the servers and the hook."""

from __future__ import annotations

from tadu.access_levels import ACCESS_LEVELS
from tadu.operation import Operation
from tadu.param import Param
from tadu.shared_params import DONE_DAYS

WORKSPACE = "directory holding tadu-workspace.toml"

LOCAL_OPERATIONS = (
    Operation(
        "board",
        "serve a kanban page for a workspace; read-only unless --allow says more",
        (
            Param("workspace", "text", WORKSPACE, required=True, metavar="DIR"),
            Param("host", "text", "address to bind (default: 127.0.0.1)", default="127.0.0.1"),
            Param(
                "port",
                "count",
                "port to bind; 0 for any free port (default: one derived from the workspace "
                "path, or any free port when that one is busy)",
            ),
            DONE_DAYS,
            Param(
                "allow",
                "choice",
                "what the page may do: read (default), write items, or admin (also archive, "
                "fmt, migrate, sync and init)",
                ACCESS_LEVELS,
                default="read",
            ),
        ),
        access="local",
        target="none",
    ),
    Operation(
        "mcp",
        "serve the backlog as MCP tools over stdio; read-only unless --allow says more",
        (
            Param("paths", "list", "repository roots (default: .)", positional=True),
            Param("workspace", "text", WORKSPACE, metavar="DIR"),
            Param(
                "allow",
                "choice",
                "what the tools may do: read (default), write items, or admin (also archive, "
                "fmt, migrate, sync and init)",
                ACCESS_LEVELS,
                default="read",
            ),
        ),
        access="local",
        target="none",
    ),
    Operation(
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
    ),
)
