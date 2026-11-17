"""The error a task-editing command stops with."""

from __future__ import annotations


class TaskCommandError(Exception):
    """A request the command refuses, with the message to print; the command exits 2."""
