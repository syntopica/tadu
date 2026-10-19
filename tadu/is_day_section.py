"""Test a level-three log heading for a section headed by one day."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.day_heading_pattern import DAY_HEADING_PATTERN

if TYPE_CHECKING:
    from datetime import date


def is_day_section(text: str, day: date) -> bool:
    """True when the heading starts with `day` as `YYYY-MM-DD`."""
    return DAY_HEADING_PATTERN.match(text) is not None and text[:10] == day.isoformat()
