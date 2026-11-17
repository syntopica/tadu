"""Split a tadu v1 title written as a bold sentence followed by its description."""

from __future__ import annotations

import re

BOLD_LEAD = re.compile(r"^\*\*([^*\n]+)\*\*\s*")


def split_bold_title(text: str) -> tuple[str, str]:
    """(title, rest): `**Title.** more` gives the bold words as the title and `more` as the rest."""
    match = BOLD_LEAD.match(text)
    if match is None:
        return text, ""
    return match.group(1).strip(), text[match.end() :].strip()
