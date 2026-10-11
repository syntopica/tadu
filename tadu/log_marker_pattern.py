"""Pattern for the marker line that separates legacy log entries."""

from __future__ import annotations

import re

LOG_MARKER_PATTERN = re.compile(r"^<!-- tadu:log v1 -->\s*$")
