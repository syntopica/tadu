"""One-line text form of a card."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.display_title_limit import DISPLAY_TITLE_LIMIT

if TYPE_CHECKING:
    from tadu.card import Card


def format_card_line(card: Card, key: str | None = None) -> str:
    """Render `<repository>:<path>:<line> [<column>] <priority or -> [due <date>] <title>`.

    A task file (format v2) is located by its id instead of path and line:
    `<repository>:<key> ...`, where `key` is the short unique prefix the caller computed.
    """
    item = card.item
    priority = item.fields.priority or "-"
    if item.fields.due is not None:
        priority += f" due {item.fields.due.isoformat()}"
    title = item.title
    if len(title) > DISPLAY_TITLE_LIMIT:
        title = title[: DISPLAY_TITLE_LIMIT - 3] + "..."
    where = key or item.key if item.path.endswith(".json") else f"{item.path}:{item.line}"
    return f"{card.repository}:{where} [{card.column}] {priority} {title}"
