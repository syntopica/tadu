"""The item filter that accepts every item."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re


def keep_every_item(match: re.Match[str]) -> bool:  # noqa: ARG001 - the filter's signature
    """True for any item first line: scan_items builds all of them."""
    return True
