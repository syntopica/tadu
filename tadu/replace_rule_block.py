"""Swap the marked block, or a legacy section, for the current block."""

from __future__ import annotations

from tadu.legacy_rule_section_pattern import LEGACY_RULE_SECTION_PATTERN
from tadu.marked_rule_block_pattern import MARKED_RULE_BLOCK_PATTERN


def replace_rule_block(text: str, block: str, adopt_legacy: bool) -> str | None:
    """New text, or None when nothing replaceable exists."""
    if MARKED_RULE_BLOCK_PATTERN.search(text):
        return MARKED_RULE_BLOCK_PATTERN.sub(lambda _: block, text, count=1)
    if adopt_legacy and LEGACY_RULE_SECTION_PATTERN.search(text):
        return LEGACY_RULE_SECTION_PATTERN.sub(lambda _: block + "\n", text, count=1)
    return None
