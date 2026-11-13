"""Combine a saved view with the filter flags given beside it."""

from __future__ import annotations

from dataclasses import fields, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.card_filter import CardFilter


def merge_filters(view: CardFilter, flags: CardFilter) -> CardFilter:
    """Start from the view; every criterion set by a flag replaces the view's."""
    given = {f.name: getattr(flags, f.name) for f in fields(flags)}
    return replace(
        view, **{key: value for key, value in given.items() if value not in (None, False)}
    )
