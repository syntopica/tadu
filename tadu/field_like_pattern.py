"""Pattern for a line that looks like an item field, whether or not it is read as one."""

from __future__ import annotations

import re

FIELD_LIKE_PATTERN = re.compile(
    r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate):(?:[ \t].*)?$"
)
