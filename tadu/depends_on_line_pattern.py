"""Pattern for a `Depends on:` paragraph indented two spaces under an item."""

from __future__ import annotations

import re

DEPENDS_ON_LINE_PATTERN = re.compile(r"^  Depends on:(.*)$")
