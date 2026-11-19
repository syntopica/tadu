"""The mcp operation."""

from __future__ import annotations

from tadu.access_levels import ACCESS_LEVELS
from tadu.operation import Operation
from tadu.param import Param
from tadu.workspace_help import WORKSPACE_HELP

MCP_OPERATION = Operation(
    "mcp",
    "serve the backlog as MCP tools over stdio; read-only unless --allow says more",
    (
        Param("paths", "list", "repository roots (default: .)", positional=True),
        Param("workspace", "text", WORKSPACE_HELP, metavar="DIR"),
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
)
