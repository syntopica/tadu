"""Swap the marked block, or a legacy section, for the current block."""

from __future__ import annotations

from tadu.dominant_newline import dominant_newline
from tadu.find_rule_markers import find_rule_markers
from tadu.legacy_rule_section_pattern import LEGACY_RULE_SECTION_PATTERN


def replace_rule_block(text: str, block: str, adopt_legacy: bool) -> str | None:
    """New text, or None when nothing replaceable exists."""
    markers = find_rule_markers(text)
    opens = [marker for marker in markers if marker.kind == "open"]
    closes = [marker for marker in markers if marker.kind == "close"]
    if opens and closes:
        return text[: opens[0].start] + block + text[closes[0].end :]
    if adopt_legacy and LEGACY_RULE_SECTION_PATTERN.search(text):
        spacer = dominant_newline(text)
        return LEGACY_RULE_SECTION_PATTERN.sub(lambda _: block + spacer, text, count=1)
    return None
