"""The instruction file `sync --agent` writes for each agent that does not read AGENTS.md alone."""

from __future__ import annotations

# name: (path relative to the root, text a new file starts with)
AGENT_RULE_FILES = {
    "gemini": ("GEMINI.md", ""),
    "copilot": (".github/copilot-instructions.md", ""),
    "cursor": (".cursor/rules/tadu.mdc", "---\nalwaysApply: true\n---\n"),
}
