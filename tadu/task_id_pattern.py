"""Pattern for a task ID: t- followed by a lowercase UUID4."""

from __future__ import annotations

import re

TASK_ID_PATTERN = re.compile(
    r"^t-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
