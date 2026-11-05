"""Pattern for a header line of `git blame --line-porcelain`: commit, original and final line."""

from __future__ import annotations

import re

BLAME_HEADER_PATTERN = re.compile(r"^[0-9a-f]{40,64} \d+ (\d+)(?: \d+)?$")
