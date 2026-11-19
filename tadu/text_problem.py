"""Refuse blank and multi-line argument values."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def text_problem(texts: Iterable[str]) -> str | None:
    """Why the values cannot be written into a backlog line, or None: blank, or not one line."""
    values = list(texts)
    if any(not value.strip() for value in values):
        return "arguments must not be blank"
    if any(len(f"{value}x".splitlines()) > 1 for value in values):
        return "arguments must be single lines"
    return None
