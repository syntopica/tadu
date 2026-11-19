"""What a GitHub login looks like: letters, digits and single inner hyphens, 39 at most."""

from __future__ import annotations

import re

GITHUB_LOGIN_PATTERN = re.compile(r"(?=.{1,39}\Z)[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
