"""Pattern for a top-level checklist item of any state, with its optional day."""

from __future__ import annotations

import re

ITEM_STATE_PATTERN = re.compile(r"^- \[( |~|!|x|-)\] (?:(\d{4}-\d{2}-\d{2}) — )?(.*)$")
