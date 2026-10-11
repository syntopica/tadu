"""Pattern for an unmarked legacy rule section, up to the next heading of any level or comment marker."""

from __future__ import annotations

import re

LEGACY_RULE_SECTION_PATTERN = re.compile(
    r"^#+ [^\n]*Continuous TODO[^\n]*"
    r"(?:\n(?:(?!#+ |<!--)[^\n]*\n)*(?:(?!#+ |<!--)[^\n]+)?)?",
    re.MULTILINE,
)
