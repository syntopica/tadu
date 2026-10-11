"""Pattern for a top-level closed checklist item, not a step indented under a parent."""

from __future__ import annotations

import re

CLOSED_ITEM_PATTERN = re.compile(r"^- \[(x|-)\] ")
