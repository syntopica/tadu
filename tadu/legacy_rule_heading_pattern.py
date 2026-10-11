"""Pattern for the heading of an unmarked legacy rule section."""

from __future__ import annotations

import re

LEGACY_RULE_HEADING_PATTERN = re.compile(r"^#+ .*Continuous TODO", re.MULTILINE)
