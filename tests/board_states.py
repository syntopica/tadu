from pathlib import Path

from tadu.board_state import BoardState
from tadu.cli import main


def board_state(
    workspace: Path, allow: str = "read", hosts: frozenset[str] = frozenset()
) -> BoardState:
    """A board's state over the workspace: 14 days of Done, token `t`, the real command line."""
    return BoardState(workspace, 14, "t", hosts, allow, main)
