"""Report keys that appear more than once."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


def duplicate_problems(kind: str, keys: Iterable[str]) -> list[str]:
    """One "duplicate <kind>: <key>" message per repeated key."""
    return [f"duplicate {kind}: {key}" for key, n in Counter(keys).items() if n > 1]
