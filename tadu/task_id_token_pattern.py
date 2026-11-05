"""Pattern for a task ID written anywhere inside a line of text."""

from __future__ import annotations

import re

TASK_ID_TOKEN_PATTERN = re.compile(
    r"(?<![\w-])t-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}(?![\w-])"
)
