"""Pattern for an item text that already starts with a bold category."""

from __future__ import annotations

import re

CATEGORY_PREFIX_PATTERN = re.compile(r"^\*\*[^*\n]+:\*\* ")
