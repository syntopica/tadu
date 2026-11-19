"""The repositories a request may see, when the workspace is to be cut to them."""

from __future__ import annotations

from contextvars import ContextVar

# Set around a tool call of a board that signs in with GitHub (see signed_in_call): the keys of
# the repositories the person reads. load_workspace then returns the workspace without the
# others, so every operation, whatever it reads, writes or prints, never meets them. None: no
# cut, as for the command line.
VISIBLE_REPOSITORIES: ContextVar[frozenset[str] | None] = ContextVar(
    "VISIBLE_REPOSITORIES", default=None
)
