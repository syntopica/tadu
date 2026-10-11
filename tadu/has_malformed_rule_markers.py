"""Whether the rule markers are present but not exactly one open then one close."""

from __future__ import annotations

from tadu.find_rule_markers import find_rule_markers


def has_malformed_rule_markers(text: str) -> bool:
    """False when there are no markers, or exactly one open followed by one close."""
    markers = find_rule_markers(text)
    opens = [marker.start for marker in markers if marker.kind == "open"]
    closes = [marker.start for marker in markers if marker.kind == "close"]
    if not markers:
        return False
    return not (len(opens) == 1 and len(closes) == 1 and opens[0] < closes[0])
