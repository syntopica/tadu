"""The shape of a function that picks the item a close request names."""

from __future__ import annotations

from collections.abc import Callable

type ItemSelector = Callable[[list[str], str], int | None]
"""Takes the backlog lines and the file name for messages; returns the item's index or None."""
