"""Pattern for an unmarked legacy rule section, up to the next top-level heading or comment marker."""

from __future__ import annotations

import re

LEGACY_RULE_SECTION_PATTERN = re.compile(
    r"^#+ [^\n]*Continuous TODO.*?(?=^#{1,2} |^<!--|\Z)", re.DOTALL | re.MULTILINE
)
