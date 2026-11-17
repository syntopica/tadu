"""Pattern for a link: a URI with a scheme and no whitespace."""

from __future__ import annotations

import re

URI_PATTERN = re.compile(r"^[a-z][a-z0-9+.-]*:\S+$")
