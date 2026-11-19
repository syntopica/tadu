"""A change the board proposes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.file_change import FileChange


@dataclass(frozen=True)
class ProposalRequest:
    """The person who asked, the operation and its arguments, and the files it changes.

    `mode` is how the repository has a pusher's change applied (see PROPOSAL_MODES).
    """

    login: str
    operation: str
    arguments: dict[str, object]
    changes: list[FileChange]
    mode: str = "pr"
