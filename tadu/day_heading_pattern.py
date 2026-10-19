"""Pattern for a log section headed by one day rather than a month."""

from __future__ import annotations

import re

DAY_HEADING_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\b")
