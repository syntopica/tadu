"""Check the marked maintenance-rule block."""

from __future__ import annotations

from pathlib import Path

from tadu.find_rule_markers import find_rule_markers
from tadu.finding import Finding
from tadu.has_malformed_rule_markers import has_malformed_rule_markers
from tadu.instruction_file import instruction_file
from tadu.legacy_rule_heading_pattern import LEGACY_RULE_HEADING_PATTERN
from tadu.read_text_exact import read_text_exact
from tadu.rule_block_version import RULE_BLOCK_VERSION


def check_rule_block(root: Path) -> tuple[Finding, ...]:
    """Report a missing file, a legacy unmarked section, no rule, malformed markers or an old block."""
    path = instruction_file(root, None)
    if path is None:
        return (Finding("R001", "warning", str(root), 0, "no AGENTS.md or CLAUDE.md"),)
    text = read_text_exact(path)
    if has_malformed_rule_markers(text):
        message = "malformed rule markers; need exactly one open then one close"
        return (Finding("R005", "error", str(path), 0, message),)
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
