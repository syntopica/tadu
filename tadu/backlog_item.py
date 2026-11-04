"""One backlog item as the board and list commands see it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from tadu.field_problem import FieldProblem
    from tadu.item_fields import ItemFields


@dataclass(frozen=True)
class BacklogItem:
    """An item with its key, 1-based inclusive line span and parsed fields."""

    key: str
    stable: bool
    path: str
    line: int
    end_line: int
    state: str
    day: date | None
    title: str
    text: str
    fields: ItemFields
    problems: tuple[FieldProblem, ...]
