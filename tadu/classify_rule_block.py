"""Classify the rule block of a readable, well-formed instruction file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.find_rule_markers import find_rule_markers
from tadu.finding import Finding
from tadu.legacy_rule_heading_pattern import LEGACY_RULE_HEADING_PATTERN
from tadu.rule_block_version import RULE_BLOCK_VERSION

if TYPE_CHECKING:
    from pathlib import Path


def classify_rule_block(path: Path, text: str) -> tuple[Finding, ...]:
    """Report a legacy unmarked section, no rule at all, or an outdated block."""
    opening = next((marker for marker in find_rule_markers(text) if marker.kind == "open"), None)
    if opening is None:
        if LEGACY_RULE_HEADING_PATTERN.search(text):
            message = "legacy rule section; run sync --adopt-legacy only if it holds just the standard rule"
            return (Finding("R002", "warning", str(path), 0, message),)
        return (Finding("R003", "error", str(path), 0, "no TODO maintenance rule"),)
    if opening.version < RULE_BLOCK_VERSION:
        message = f"rule block v{opening.version}; current is v{RULE_BLOCK_VERSION}"
        return (Finding("R004", "warning", str(path), 0, message),)
    return ()
