"""The list_items MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.card_json import card_json
from tadu.card_matches import card_matches
from tadu.mcp_load_cards import mcp_load_cards

if TYPE_CHECKING:
    from tadu.card_filter import CardFilter
    from tadu.mcp_scope import McpScope


def mcp_list_items(scope: McpScope, card_filter: CardFilter) -> dict[str, object]:
    """The matching cards as `tadu list --json` prints them, and the skipped repositories."""
    cards, problems = mcp_load_cards(scope)
    return {
        "items": [card_json(card) for card in cards if card_matches(card, card_filter)],
        "problems": [{"repository": p.repository, "message": p.message} for p in problems],
    }
