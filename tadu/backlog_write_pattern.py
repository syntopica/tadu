"""Patterns for a shell command that rewrites a backlog file."""

from __future__ import annotations

import re

BACKLOG_NAME_PATTERN = re.compile(r"TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl")
SHELL_WRITE_PATTERN = re.compile(
    r"open\(|write_text|sed\s+-i|\btee\b|\bmv\b|\bcp\b|\bpatch\b|\bperl\s+-[a-z]*i"
    r"|>\s*(?:\"[^\"]*|'[^']*|[^\s;&|<>\"']*)(?:TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl)"
)
BACKLOG_PATH_PATTERN = re.compile(
    r"((?:[^;&|<>\"'=(]*/)?)(?:TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl)"
)
TADU_CLOSE_WRITE_PATTERN = re.compile(r"\btadu\s+close\b(?=.*--write)", re.DOTALL)
LEADING_CD_PATTERN = re.compile(r"\s*cd\s+([^\s;&|]+)\s*(?:&&|;)")
