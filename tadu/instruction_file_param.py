"""The instruction-file override shared by init and sync."""

from __future__ import annotations

from tadu.param import Param

INSTRUCTION_FILE_PARAM = Param(
    "file", "text", "instruction file (default: AGENTS.override.md, then AGENTS.md, then CLAUDE.md)"
)
