"""The error that stops `tadu show --history`."""

from __future__ import annotations


class HistoryError(Exception):
    """History could not be read: no git, a checkout outside a repository, or git failed."""
