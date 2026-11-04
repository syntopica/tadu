"""Validate an Estimate field value."""

from __future__ import annotations

import re


def check_estimate_value(value: str) -> str | None:
    """A problem message, or None when the value is 1 to 9 digits and not zero."""
    if re.fullmatch(r"[1-9][0-9]{0,8}", value):
        return None
    return "Estimate is not a positive whole number of minutes"
