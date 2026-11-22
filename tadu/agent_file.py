"""The instruction file `sync` writes for an agent named with --agent."""

from __future__ import annotations

from tadu.agent_rule_files import AGENT_RULE_FILES


def agent_file(file: str | None, agent: str | None) -> str | None:
    """The named agent's own file, which wins over a --file a config file set; else `file`."""
    return AGENT_RULE_FILES[agent][0] if agent else file
