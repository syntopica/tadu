"""The part of a backlog text one change touched, as whole items."""

from __future__ import annotations

from tadu.common_prefix_length import common_prefix_length
from tadu.common_suffix_length import common_suffix_length


def changed_window(before: str, after: str) -> str:
    """The lines of `before` between the start and the end both texts share, widened to items.

    It reaches back to the line before the first changed one (an insertion counts for the item it
    follows) and on to the start of that item; forward to the end of the item the change ends in.
    An item starts at an unindented line; blank and indented lines belong to the item above.
    """
    start = common_prefix_length(before, after)
    limit = min(len(before), len(after)) - start
    end = len(before) - common_suffix_length(before, after, limit)
    line = before.rfind("\n", 0, start) + 1
    first = before.rfind("\n", 0, line - 1) + 1 if line > 0 else 0
    while first > 0 and before[first : first + 1] in (" ", "\t", "\n"):
        first = before.rfind("\n", 0, first - 1) + 1
    stop = before.find("\n", max(end - 1, first))
    stop = len(before) if stop == -1 else stop
    while stop < len(before):
        after_line = before.find("\n", stop + 1)
        following = len(before) if after_line == -1 else after_line
        text = before[stop + 1 : following]
        if text.strip() and text[0] not in " \t":
            break
        stop = following
    return before[first:stop]
