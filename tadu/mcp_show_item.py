"""The show_item MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp.server.mcpserver.exceptions import ToolError

from tadu.card_json import card_json
from tadu.mcp_load_cards import mcp_load_cards

if TYPE_CHECKING:
    from tadu.mcp_scope import McpScope


def mcp_show_item(scope: McpScope, key: str) -> dict[str, object]:
    """The first card whose key matches, with the number of matches; a ToolError if none."""
    cards, _ = mcp_load_cards(scope)
    found = [card for card in cards if card.item.key == key]
    if not found:
        msg = f"no item {key}"
        raise ToolError(msg)
    return {"item": card_json(found[0]), "matches": len(found)}
