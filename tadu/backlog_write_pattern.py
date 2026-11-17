"""Patterns for a shell command that rewrites a backlog file."""

from __future__ import annotations

import re

BACKLOG_NAME_PATTERN = re.compile(
    r"TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl|todo/(?:[^\s;&|<>\"']*/)?[^\s;&|<>\"']*\.json"
)
SHELL_WRITE_PATTERN = re.compile(
    r"open\(|write_text|sed\s+-i|\btee\b|\bmv\b|\bcp\b|\bpatch\b|\bperl\s+-[a-z]*i"
    r"|>\s*(?:\"[^\"]*|'[^']*|[^\s;&|<>\"']*)"
    r"(?:TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl|todo/[^\s;&|<>\"']*\.json)"
)
BACKLOG_PATH_PATTERN = re.compile(
    r"((?:[^;&|<>\"'=(]*/)?)(?:TODO(?:_LOG)?\.md|TODO_HISTORY_INDEX\.jsonl|todo/[^\s;&|<>\"']*\.json)"
)
TADU_WRITE_PATTERN = re.compile(
    r"\btadu\s+(?:close|add|set|claim|archive|fmt|migrate)\b(?=.*--write)", re.DOTALL
)
LEADING_CD_PATTERN = re.compile(r"\s*cd\s+([^\s;&|]+)\s*(?:&&|;)")
