"""Values the kind filter takes: each kind, and `unclassified` for items without one."""

from __future__ import annotations

from tadu.kinds import KINDS

KIND_FILTERS = (*KINDS, "unclassified")
