"""Turn the list_items `where` argument into a card filter."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from tadu.card_filter import CardFilter

if TYPE_CHECKING:
    from tadu.mcp_where import McpWhere


def mcp_card_filter(where: McpWhere | None) -> CardFilter:
    """The card filter holding the criteria set in `where`; an empty one when it is absent."""
    if where is None:
        return CardFilter()
    return CardFilter(**asdict(where))
