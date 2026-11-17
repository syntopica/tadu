"""One-line text form of a card."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.display_title_limit import DISPLAY_TITLE_LIMIT

if TYPE_CHECKING:
    from tadu.card import Card


def format_card_line(card: Card) -> str:
    """Render `<repository>:<path>:<line> [<column>] <priority or -> <title>`.

    An item with a `Kind:` shows it in the brackets, `[backlog/decision]`; one without
    prints exactly as before kinds existed.
    """
    item = card.item
    priority = item.fields.priority or "-"
    where = card.column if item.fields.kind is None else f"{card.column}/{item.fields.kind}"
    title = item.title
    if len(title) > DISPLAY_TITLE_LIMIT:
        title = title[: DISPLAY_TITLE_LIMIT - 3] + "..."
    return f"{card.repository}:{item.path}:{item.line} [{where}] {priority} {title}"
