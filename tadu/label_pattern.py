"""Pattern for a lowercase slug label."""

from __future__ import annotations

import re

LABEL_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
