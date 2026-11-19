"""The history of the item a card shows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_checkout import git_checkout
from tadu.markdown_history import markdown_history
from tadu.task_history import task_history
from tadu.todo_layout import TASK_SUFFIX

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.card import Card
    from tadu.history_event import HistoryEvent


def card_history(card: Card, root: Path) -> tuple[tuple[HistoryEvent, ...], bool]:
    """Each change to the card's item, newest first, and whether the clone is shallow.

    `root` is the card's checkout. A shallow clone's history stops at its oldest commit.
    HistoryError when git cannot tell the history.
    """
    prefix, shallow = git_checkout(root)
    history = task_history if card.item.path.endswith(TASK_SUFFIX) else markdown_history
    return history(root, prefix, card.item, card.repository), shallow
