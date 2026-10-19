"""Test a level-two log heading for a year or a legacy month."""

from __future__ import annotations

from tadu.year_heading_pattern import YEAR_HEADING_PATTERN


def is_year_heading(text: str) -> bool:
    """True for `YYYY` or `YYYY-MM`."""
    return YEAR_HEADING_PATTERN.match(text) is not None
