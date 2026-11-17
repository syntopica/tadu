"""Build a check for a value that must be one of a fixed set."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def choice_check(choices: tuple[object, ...]) -> Callable[[object], str | None]:
    """A check returning a message unless the value is one of `choices`."""
    allowed = ", ".join(str(choice) for choice in choices)

    def check(value: object) -> str | None:
        if isinstance(value, bool) or value not in choices:
            return f"must be one of {allowed}"
        return None

    return check
