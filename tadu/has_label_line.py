"""Detect a dedicated, non-empty label line inside a log entry."""

from __future__ import annotations

import re


def has_label_line(lines: list[str], label: str) -> bool:
    """True when a line starts with the label and carries content, here or on the next indented line."""
    pattern = re.compile(rf"^\s*(?:- )?{re.escape(label)}(.*)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if match is None:
            continue
        if match.group(1).strip():
            return True
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if (
            following[:1] in (" ", "\t")
            and following.strip()
            and not following.lstrip().startswith("- ")
        ):
            return True
    return False
