"""Cards for an MCP tool call."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from mcp.server.mcpserver.exceptions import ToolError

from tadu.load_cards import load_cards
from tadu.workspace_error import WorkspaceError

if TYPE_CHECKING:
    from tadu.card import Card
    from tadu.mcp_scope import McpScope
    from tadu.scan_problem import ScanProblem


def mcp_load_cards(scope: McpScope) -> tuple[tuple[Card, ...], tuple[ScanProblem, ...]]:
    """Rescan the scope as of today; a bad workspace becomes a ToolError."""
    today = datetime.now(UTC).astimezone().date()
    try:
        cards, problems, _ = load_cards(scope.paths, scope.workspace, scope.done_days, today)
    except WorkspaceError as error:
        raise ToolError(str(error)) from error
    return cards, problems
