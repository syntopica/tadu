"""Pattern for an optional field line indented two spaces under an item."""

from __future__ import annotations

import re

FIELD_LINE_PATTERN = re.compile(r"^  (ID|Priority|Assignees|Due|Labels|Queue|Estimate): (.*)$")
