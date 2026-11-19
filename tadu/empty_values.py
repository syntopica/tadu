"""The values a task key holds when it holds nothing: the writer leaves such keys out."""

from __future__ import annotations

EMPTY_VALUES: tuple[object, ...] = (None, "", [], {})
