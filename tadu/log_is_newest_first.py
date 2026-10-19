"""Infer the order a log keeps its dated entries in."""

from __future__ import annotations

from itertools import pairwise

from tadu.log_entry_pattern import LOG_ENTRY_PATTERN


def log_is_newest_first(lines: list[str], fenced: list[bool]) -> bool:
    """True when descending neighbour pairs of entry dates outnumber ascending ones."""
    dates = [
        match.group(2)
        for line, inside in zip(lines, fenced, strict=True)
        if not inside and (match := LOG_ENTRY_PATTERN.match(line))
    ]
    falling = sum(1 for a, b in pairwise(dates) if a > b)
    rising = sum(1 for a, b in pairwise(dates) if a < b)
    return falling > rising
