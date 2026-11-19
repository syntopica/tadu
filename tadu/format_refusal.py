"""Refuse the options of the other backlog format."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.empty_values import EMPTY_VALUES

if TYPE_CHECKING:
    import argparse

    from tadu.operation import Operation


def format_refusal(operation: Operation, args: argparse.Namespace, format_: int) -> str | None:
    """Why the options given do not fit a backlog of `format_` (1 or 2), or None.

    An option only the other format takes would be dropped in silence, so it is refused
    instead, naming every such option given.
    """
    given = [
        param.flag
        for param in operation.params
        if param.format not in (0, format_)
        and getattr(args, param.name, None) not in (*EMPTY_VALUES, False)
    ]
    if not given:
        return None
    backlog = "a TODO.md backlog" if format_ == 1 else "a task backlog"
    return f"{backlog} takes no {', '.join(given)}"
