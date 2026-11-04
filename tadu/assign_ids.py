"""Give several items an ID, in memory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.insert_id_field import insert_id_field

if TYPE_CHECKING:
    from collections.abc import Callable


def assign_ids(lines: list[str], firsts: list[int], make_id: Callable[[], str]) -> list[str]:
    """The lines with a fresh ID paragraph in each item at `firsts`, last item first."""
    result = lines
    for first in sorted(firsts, reverse=True):
        result = insert_id_field(result, first, make_id())
    return result
