"""Pattern for an item text that already starts with its own ISO date and a dash."""

from __future__ import annotations

import re

ITEM_DATE_PREFIX_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} [—-] (?=\*\*[^*\n]+:\*\* )")
