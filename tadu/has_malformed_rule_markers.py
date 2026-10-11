"""Whether the rule markers are present but not exactly one open then one close."""

from __future__ import annotations

from tadu.rule_block_close_pattern import RULE_BLOCK_CLOSE_PATTERN
from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN


def has_malformed_rule_markers(text: str) -> bool:
    """False when there are no markers, or exactly one open followed by one close."""
    opens = [match.start() for match in RULE_BLOCK_OPEN_PATTERN.finditer(text)]
    closes = [match.start() for match in RULE_BLOCK_CLOSE_PATTERN.finditer(text)]
    if not opens and not closes:
        return False
    return not (len(opens) == 1 and len(closes) == 1 and opens[0] < closes[0])
