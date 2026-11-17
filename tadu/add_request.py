"""A new backlog item as asked for."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddRequest:
    """The title, its `##` category, field lines in order and note paragraphs."""

    title: str
    category: str | None
    fields: tuple[tuple[str, str], ...]
    notes: tuple[str, ...]
