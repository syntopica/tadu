"""Pattern for a line that ends a log entry: a top-level item or a heading."""

from __future__ import annotations

import re

ENTRY_BOUNDARY_PATTERN = re.compile(r"^(?:- |#{1,6} )")
