"""A named filter set kept in the workspace file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card_filter import CardFilter


@dataclass(frozen=True)
class ViewEntry:
    """The view's name and the filter it selects."""

    name: str
    card_filter: CardFilter
