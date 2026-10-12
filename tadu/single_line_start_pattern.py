"""Pattern for a line that is a whole element on its own: a heading or an HTML comment."""

from __future__ import annotations

import re

SINGLE_LINE_START_PATTERN = re.compile(r"^[ \t]*(?:#{1,6}[ \t]|<!--)")
