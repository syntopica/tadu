"""Every item of one version of a Markdown backlog file."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from tadu.scan_items import scan_items

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

ALL_STATES = " ~!x-"


@lru_cache(maxsize=16)
def markdown_items(text: str, repository: str, path: str) -> tuple[BacklogItem, ...]:
    """Open and closed top-level items of `text`, keyed as `tadu list` keys them.

    A walk through history meets each version twice, once after a commit and once before the
    next, so recent results are kept.
    """
    return scan_items(text.split("\n"), repository, path, ALL_STATES) if text else ()
