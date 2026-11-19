"""The checkouts a request reads from somewhere else than the local file says."""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Set around the run of a change a team board proposes (see propose_call): the checkout paths of
# repositories by key, which parse_paths then returns instead of the ones the local file names,
# so the change lands on a copy and never on the server's checkout. None: no redirect.
REDIRECTED_CHECKOUTS: ContextVar[dict[str, Path] | None] = ContextVar(
    "REDIRECTED_CHECKOUTS", default=None
)
