"""The show_item MCP tool handler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tadu.mcp_show_item import mcp_show_item

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


@dataclass(frozen=True)
class McpShowItemTool:
    """The show_item handler bound to one scope; register its `show_item` method."""

    scope: McpScope

    def show_item(self, key: str) -> dict[str, object]:
        """Show one backlog item by the key `list_items` reports."""
        return mcp_show_item(self.scope, key)
