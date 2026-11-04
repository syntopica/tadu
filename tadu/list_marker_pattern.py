"""Pattern for a stripped line that starts a bullet or numbered list item."""

from __future__ import annotations

import re

LIST_MARKER_PATTERN = re.compile(r"^(?:[-*+]|\d+[.)])[ \t]")
