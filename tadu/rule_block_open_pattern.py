"""Pattern for the opening marker of the rule block."""

from __future__ import annotations

import re

RULE_BLOCK_OPEN_PATTERN = re.compile(r"<!-- tadu:rule v(\d+) -->")
