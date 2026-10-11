"""The review statuses a history index record may carry."""

from __future__ import annotations

REVIEW_STATUSES = frozenset({"complete", "partial", "inaccessible", "irrelevant"})
