"""Pattern for the whole marked rule block, markers included."""

from __future__ import annotations

import re

MARKED_RULE_BLOCK_PATTERN = re.compile(
    r"<!-- tadu:rule v\d+ -->.*?<!-- /tadu:rule -->\n?", re.DOTALL
)
