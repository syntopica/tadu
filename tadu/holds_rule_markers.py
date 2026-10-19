"""Detect an instruction file that already carries the rule markers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.find_rule_markers import find_rule_markers
from tadu.read_text_exact import read_text_exact
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def holds_rule_markers(path: Path) -> bool:
    """True when the file reads and has at least one rule marker line."""
    try:
        return bool(find_rule_markers(read_text_exact(path)))
    except UnreadableFileError:
        return False
