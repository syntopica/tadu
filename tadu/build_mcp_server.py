"""A read-only MCP server over one scope's backlog items."""

from __future__ import annotations

from importlib.metadata import version
from typing import TYPE_CHECKING

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from tadu.columns import COLUMNS
from tadu.mcp_list_items_tool import McpListItemsTool
from tadu.mcp_show_item_tool import McpShowItemTool
from tadu.priorities import PRIORITIES

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


def build_mcp_server(scope: McpScope) -> MCPServer[object]:
    """Register `list_items` and `show_item`, which read the backlogs and never write."""
    server: MCPServer[object] = MCPServer(
        "tadu",
        version=version("tadu"),
        instructions="Read the open and recently closed items of tadu backlogs.",
    )
    read_only = ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False)
    server.add_tool(
        McpListItemsTool(scope).list_items,
        description=(
            "List backlog items as `tadu list --json` does, with the repositories that could "
            "not be scanned. Every criterion set in `where` must hold; unknown criteria are "
            f"rejected. `column` is one of {', '.join(COLUMNS)}; `priority` one of "
            f"{', '.join(PRIORITIES)}; `due_before` is YYYY-MM-DD."
        ),
        annotations=read_only,
    )
    server.add_tool(McpShowItemTool(scope).show_item, annotations=read_only)
    return server
