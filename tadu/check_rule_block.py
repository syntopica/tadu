"""Check the marked maintenance-rule block."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.classify_rule_block import classify_rule_block
from tadu.finding import Finding
from tadu.has_malformed_rule_markers import has_malformed_rule_markers
from tadu.instruction_file import instruction_file
from tadu.read_text_exact import read_text_exact

if TYPE_CHECKING:
    from pathlib import Path


def check_rule_block(root: Path) -> tuple[Finding, ...]:
    """Report a missing file, a legacy unmarked section, no rule, malformed markers or an old block."""
    path = instruction_file(root, None)
    if path is None:
        return (Finding("R001", "warning", str(root), 0, "no AGENTS.md or CLAUDE.md"),)
    text = read_text_exact(path)
    if has_malformed_rule_markers(text):
        message = "malformed rule markers; need exactly one open then one close"
        return (Finding("R005", "error", str(path), 0, message),)
    return classify_rule_block(path, text)
