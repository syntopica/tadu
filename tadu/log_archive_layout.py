"""Where a Markdown backlog keeps the complete old years of its log."""

from __future__ import annotations

import re

LOG_ARCHIVE_DIR = ("docs", "todo-log")
LOG_ARCHIVE_YEAR_PATTERN = re.compile(r"^(\d{4})\.md$")
