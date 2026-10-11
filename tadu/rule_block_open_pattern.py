"""Pattern for a line that is only the opening marker of the rule block."""

from __future__ import annotations

import re

RULE_BLOCK_OPEN_PATTERN = re.compile(r"^[ \t]*<!-- tadu:rule v(\d+) -->[ \t]*$")
