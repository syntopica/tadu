"""What a board signing in with GitHub shows one person of the workspace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.local_config import LocalConfig
    from tadu.scan_problem import ScanProblem
    from tadu.workspace import Workspace


@dataclass(frozen=True)
class PayloadView:
    """The cut workspace, the local settings as theirs, problems to tell, their login.

    The workspace holds only what the person may see; `me` in the local settings is
    the person with their GitHub login.
    """

    workspace: Workspace
    local: LocalConfig
    problems: tuple[ScanProblem, ...]
    user: str
