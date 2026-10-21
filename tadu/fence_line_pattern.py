"""Pattern for a line that opens or closes a fenced code block."""

from __future__ import annotations

import re

# CommonMark 4.5 forbids backticks only in a backtick fence's info string.
FENCE_LINE_PATTERN = re.compile(r"^ {0,3}(`{3,}(?=[^`]*$)|~{3,})")
