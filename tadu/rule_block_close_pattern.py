"""Pattern for a line that is only the closing marker of the rule block."""

from __future__ import annotations

import re

RULE_BLOCK_CLOSE_PATTERN = re.compile(r"^[ \t]*<!-- /tadu:rule -->[ \t]*$")
