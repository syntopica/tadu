"""The first of several checks that found something."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def first_problem(problems: Iterable[str | None]) -> str | None:
    """The first problem that is not None, or None when every check passed."""
    return next((problem for problem in problems if problem is not None), None)
