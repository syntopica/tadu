"""A GitHub token that no longer works."""

from __future__ import annotations


class SignedOutError(Exception):
    """GitHub refused the session's token: it was revoked or has expired."""
