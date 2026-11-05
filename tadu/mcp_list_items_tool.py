"""The list_items MCP tool handler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tadu.mcp_card_filter import mcp_card_filter
from tadu.mcp_list_items import mcp_list_items
from tadu.mcp_where import McpWhere  # noqa: TC001

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


@dataclass(frozen=True)
class McpListItemsTool:
    """The list_items handler bound to one scope; register its `list_items` method.

    The server builds the tool's input schema from the method's annotations, so `McpWhere`
    is imported at runtime.
    """

    scope: McpScope

    def list_items(self, where: McpWhere | None = None) -> dict[str, object]:
        """List backlog items; every criterion set in `where` must hold."""
        return mcp_list_items(self.scope, mcp_card_filter(where))
