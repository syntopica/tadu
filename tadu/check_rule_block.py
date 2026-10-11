"""Check the marked maintenance-rule block."""

from __future__ import annotations

from pathlib import Path

from tadu.finding import Finding
from tadu.has_malformed_rule_markers import has_malformed_rule_markers
from tadu.instruction_file import instruction_file
from tadu.legacy_rule_heading_pattern import LEGACY_RULE_HEADING_PATTERN
from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN
from tadu.rule_block_version import RULE_BLOCK_VERSION


def check_rule_block(root: Path) -> tuple[Finding, ...]:
    """Report a missing file, a legacy unmarked section, no rule, malformed markers or an old block."""
    path = instruction_file(root, None)
    if path is None:
        return (Finding("R001", "warning", str(root), 0, "no AGENTS.md or CLAUDE.md"),)
    text = path.read_text(encoding="utf-8")
    if has_malformed_rule_markers(text):
        message = "malformed rule markers; need exactly one open then one close"
        return (Finding("R005", "error", str(path), 0, message),)
    match = RULE_BLOCK_OPEN_PATTERN.search(text)
    if match is None:
        if LEGACY_RULE_HEADING_PATTERN.search(text):
            message = "legacy rule section; run sync --adopt-legacy"
            return (Finding("R002", "warning", str(path), 0, message),)
        return (Finding("R003", "error", str(path), 0, "no TODO maintenance rule"),)
    if int(match.group(1)) < RULE_BLOCK_VERSION:
        message = f"rule block v{match.group(1)}; current is v{RULE_BLOCK_VERSION}"
        return (Finding("R004", "warning", str(path), 0, message),)
    return ()
