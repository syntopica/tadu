"""Bind addresses that only this machine can reach."""

from __future__ import annotations

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost"})
