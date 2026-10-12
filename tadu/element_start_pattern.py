"""Pattern for a line that starts a Markdown element rather than continuing one."""

from __future__ import annotations

import re

ELEMENT_START_PATTERN = re.compile(
    r"^[ \t]*(?:[-*+]|\d+[.)])(?:[ \t]+|$)|^[ \t]*(?:#{1,6}[ \t]|<!--)"
)
