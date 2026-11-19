"""How alike two versions of a backlog item are."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from tadu.body_lines import body_lines
from tadu.category_prefix_pattern import CATEGORY_PREFIX_PATTERN

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem

MIN_KEPT_LINES = 2


def item_similarity(old: BacklogItem, new: BacklogItem) -> float:
    """0 to 1: the likeness of the titles, or the share of the old body lines `new` kept.

    Titles are compared without the **Category:** prefix and the final period that closing
    adds and drops. Kept lines count only for a body of two lines or more, so one common line
    such as a `Done when:` does not make two items alike.
    """
    titles = [
        CATEGORY_PREFIX_PATTERN.sub("", item.title, count=1).rstrip(".").casefold()
        for item in (old, new)
    ]
    likeness = SequenceMatcher(None, titles[0], titles[1]).ratio()
    old_lines, new_lines = body_lines(old), set(body_lines(new))
    if len(old_lines) < MIN_KEPT_LINES:
        return likeness
    return max(likeness, sum(line in new_lines for line in old_lines) / len(old_lines))
