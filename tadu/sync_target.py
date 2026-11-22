"""Choose the instruction file sync works on and the text a new one starts with."""

from __future__ import annotations

from pathlib import Path

from tadu.agent_rule_files import AGENT_RULE_FILES
from tadu.instruction_file import instruction_file


def sync_target(root: Path, file: str | None) -> tuple[Path, str]:
    """The instruction file, and the opening an agent's own file needs, such as Cursor's front matter."""
    candidate = instruction_file(root, file) or root / "AGENTS.md"
    openings = [text for name, text in AGENT_RULE_FILES.values() if Path(name) == Path(file or "")]
    return candidate, "".join(openings)
