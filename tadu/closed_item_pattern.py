"""Pattern for a closed checklist item."""

from __future__ import annotations

import re

CLOSED_ITEM_PATTERN = re.compile(r"^\s*- \[(x|-)\] ")
