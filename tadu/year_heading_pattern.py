"""Pattern for a level-two log heading that is a year or a legacy month."""

from __future__ import annotations

import re

YEAR_HEADING_PATTERN = re.compile(r"^\d{4}(?:-\d{2})?$")
