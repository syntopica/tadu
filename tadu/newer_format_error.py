"""The error a command stops with on a backlog newer than this tadu."""

from __future__ import annotations


class NewerFormatError(Exception):
    """A backlog written in a format newer than this tadu reads; the command exits 2."""
