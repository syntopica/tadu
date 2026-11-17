"""Count cards per section as short text."""

from __future__ import annotations

from collections import Counter

VERBS = {"do": "to do", "decide": "to decide", "chase": "to chase", "check": "to check"}


def section_counts(sections: list[str]) -> str:
    """`3 to decide, 1 to chase, 2 blocked` in section order, nonzero counts only."""
    counts = Counter(sections)
    order = ("do", "decide", "chase", "check", "blocked")
    return ", ".join(f"{counts[name]} {VERBS.get(name, name)}" for name in order if counts[name])
