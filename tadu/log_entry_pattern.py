"""Pattern for a dated closed-work entry in TODO_LOG.md."""

from __future__ import annotations

import re

LOG_ENTRY_PATTERN = re.compile(r"^- \[(x|-)\] \d{4}-\d{2}-\d{2} ")
