"""Pattern for a top-level open checklist item: pending, partial or blocked."""

from __future__ import annotations

import re

OPEN_ITEM_PATTERN = re.compile(r"^- \[( |~|!)\] ")
