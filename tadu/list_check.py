"""Build a check for a list value whose elements share one rule."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def list_check(
    element_ok: Callable[[str], bool], what: str, *, unique: bool = True
) -> Callable[[object], str | None]:
    """A check returning a message unless the value is a non-empty list of valid strings."""

    def check(value: object) -> str | None:
        if not isinstance(value, list) or not value:
            return f"must be a non-empty list of {what}"
        if not all(isinstance(item, str) and element_ok(item) for item in value):
            return f"must be a list of {what}"
        if unique and len(set(value)) != len(value):
            return "must not repeat an element"
        return None

    return check
