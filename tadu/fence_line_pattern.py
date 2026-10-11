"""Pattern for a line that opens or closes a fenced code block."""

from __future__ import annotations

import re

FENCE_LINE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
