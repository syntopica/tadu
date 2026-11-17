"""The category a tadu v1 item names in its **Category:** prefix."""

from __future__ import annotations

import re

from tadu.category_prefix_pattern import CATEGORY_PREFIX_PATTERN


def title_category(title: str) -> str | None:
    """The prefix as a slug (**CI portability:** gives ci-portability), or None without one."""
    match = CATEGORY_PREFIX_PATTERN.match(title)
    if match is None:
        return None
    return re.sub(r"[^a-z0-9]+", "-", match.group(0)[2:-4].lower()).strip("-") or None
