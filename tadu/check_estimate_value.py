"""Validate an Estimate field value."""

from __future__ import annotations


def check_estimate_value(value: str) -> str | None:
    """A problem message, or None when the value is a positive whole number."""
    if value.isascii() and value.isdigit() and int(value) > 0:
        return None
    return "Estimate is not a positive whole number of minutes"
