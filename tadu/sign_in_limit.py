"""Argparse type for how often one address may sign in."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from limits import RateLimitItem

OFF = ("off", "none")


def sign_in_limit(text: str) -> tuple[RateLimitItem, ...]:
    """The limits, as the `limits` library reads them; none for `off`.

    Written like `10/minute`, `10 per minute` or `10/minute;100/hour`. A limit of 0 would refuse everyone, so it is rejected: `off` turns limiting off.
    """
    if text.strip().lower() in OFF:
        return ()
    from limits import parse_many  # noqa: PLC0415 - only when given: every command builds the parser

    try:
        items = tuple(parse_many(text))
    except ValueError:
        items = ()
    if not items or any(item.amount < 1 for item in items):
        msg = f"must be like 10/minute or 10/minute;100/hour, or off: {text}"
        raise argparse.ArgumentTypeError(msg)
    return items
