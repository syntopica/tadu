"""Detect a dedicated label line inside a log entry."""

from __future__ import annotations

import re


def has_label_line(lines: list[str], label: str) -> bool:
    """True when a line starts with the label, after indentation and an optional bullet."""
    pattern = re.compile(rf"^\s*(?:- )?{re.escape(label)}")
    return any(pattern.match(line) for line in lines)
