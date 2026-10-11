"""Pattern for the marker line that dates the legacy boundary of the log."""

from __future__ import annotations

import re

LOG_MARKER_PATTERN = re.compile(r"^<!-- tadu:log v1 since (\S+) -->\s*$")
